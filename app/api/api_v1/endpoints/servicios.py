from fastapi import APIRouter, Depends, HTTPException, status, Form
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.deps import get_current_persona
from app.models.persona import Persona
from app.schemas.solicitud_servicio import (
    SolicitudServicioResponse,
    SolicitudServicioCreate,
    TallerSugeridoResponse,
    TallerBasicInfo
)
from app.services import solicitud_servicio_service
from app.crud import (
    solicitud_servicio as solicitud_servicio_crud,
    diagnostico as diagnostico_crud,
    solicitud_diagnostico as solicitud_diagnostico_crud,
    taller as taller_crud
)
from geoalchemy2.shape import to_shape

router = APIRouter(prefix="/servicios", tags=["Servicios"])


@router.post("/{diagnostico_id}/generar-solicitudes", status_code=status.HTTP_201_CREATED)
async def generar_solicitudes_automaticas(
    diagnostico_id: int,
    current_persona: Persona = Depends(get_current_persona),
    db: AsyncSession = Depends(get_db)
):
    """
    Genera solicitudes de servicio automáticas para talleres sugeridos
    basándose en las especialidades requeridas y la ubicación del cliente
    """
    try:
        resultado = await solicitud_servicio_service.crear_solicitudes_servicio_automaticas(
            db=db,
            id_diagnostico=diagnostico_id,
            id_persona=current_persona.id
        )
        return resultado
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar solicitudes: {str(e)}")


@router.get("/{diagnostico_id}/talleres-sugeridos", response_model=List[TallerSugeridoResponse])
async def listar_talleres_sugeridos(
    diagnostico_id: int,
    current_persona: Persona = Depends(get_current_persona),
    db: AsyncSession = Depends(get_db)
):
    """
    Lista todos los talleres sugeridos y otros talleres cercanos,
    indicando cuáles ya tienen solicitud de servicio
    """
    # Verificar que el diagnóstico pertenece al usuario
    diagnostico = await diagnostico_crud.get(db, diagnostico_id)
    if not diagnostico:
        raise HTTPException(status_code=404, detail="Diagnóstico no encontrado")
    
    solicitud_diag = await solicitud_diagnostico_crud.get(db, diagnostico.id_solicitud_diagnostico)
    if not solicitud_diag or solicitud_diag.id_persona != current_persona.id:
        raise HTTPException(status_code=403, detail="No autorizado")
    
    # Obtener ubicación del cliente
    if not solicitud_diag.ubicacion:
        raise HTTPException(status_code=400, detail="La solicitud no tiene ubicación")
    
    point = to_shape(solicitud_diag.ubicacion)
    ubicacion_cliente = (point.y, point.x)
    
    # Obtener especialidades requeridas
    especialidades_ids = await solicitud_servicio_service.obtener_especialidades_requeridas(
        db, diagnostico_id
    )
    
    # Obtener distancia máxima
    distancia_maxima = await solicitud_servicio_service.obtener_distancia_maxima(db)
    
    # Buscar talleres cercanos con especialidades
    talleres_info = await solicitud_servicio_service.buscar_talleres_cercanos_con_especialidades(
        db,
        ubicacion_cliente,
        especialidades_ids,
        distancia_maxima
    )
    
    # Obtener solicitudes existentes
    solicitudes_existentes = await solicitud_servicio_crud.get_by_diagnostico(db, diagnostico_id)
    solicitudes_map = {s.id_taller: s for s in solicitudes_existentes}
    
    # Construir respuesta
    resultado = []
    for taller_info in talleres_info:
        taller = taller_info['taller']
        tiene_solicitud = taller.id in solicitudes_map
        
        resultado.append({
            'taller': TallerBasicInfo(
                id=taller.id,
                nombre=taller.nombre,
                telefono=taller.telefono,
                email=taller.email,
                puntos=float(taller.puntos)
            ),
            'distancia_km': taller_info['distancia_km'],
            'tiene_solicitud': tiene_solicitud,
            'solicitud_id': solicitudes_map[taller.id].id if tiene_solicitud else None,
            'especialidades_disponibles': taller_info['especialidades_disponibles']
        })
    
    return resultado


@router.post("/{diagnostico_id}/solicitar-taller", status_code=status.HTTP_201_CREATED)
async def solicitar_servicio_taller(
    diagnostico_id: int,
    id_taller: int = Form(...),
    comentario: Optional[str] = Form(None),
    current_persona: Persona = Depends(get_current_persona),
    db: AsyncSession = Depends(get_db)
):
    """
    Crea una solicitud de servicio manual para un taller específico
    (elegido por el conductor)
    """
    try:
        solicitud = await solicitud_servicio_service.crear_solicitud_servicio_manual(
            db=db,
            id_diagnostico=diagnostico_id,
            id_taller=id_taller,
            id_persona=current_persona.id,
            comentario=comentario
        )
        
        # Convertir ubicacion a string
        if solicitud.ubicacion:
            point = to_shape(solicitud.ubicacion)
            solicitud.ubicacion = f"{point.y},{point.x}"
        
        return solicitud
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{diagnostico_id}/solicitudes", response_model=List[SolicitudServicioResponse])
async def listar_solicitudes_servicio(
    diagnostico_id: int,
    current_persona: Persona = Depends(get_current_persona),
    db: AsyncSession = Depends(get_db)
):
    """
    Lista todas las solicitudes de servicio para un diagnóstico
    """
    # Verificar que el diagnóstico pertenece al usuario
    diagnostico = await diagnostico_crud.get(db, diagnostico_id)
    if not diagnostico:
        raise HTTPException(status_code=404, detail="Diagnóstico no encontrado")
    
    solicitud_diag = await solicitud_diagnostico_crud.get(db, diagnostico.id_solicitud_diagnostico)
    if not solicitud_diag or solicitud_diag.id_persona != current_persona.id:
        raise HTTPException(status_code=403, detail="No autorizado")
    
    # Obtener solicitudes
    solicitudes = await solicitud_servicio_crud.get_by_diagnostico(db, diagnostico_id)
    
    # Convertir ubicaciones a string
    for solicitud in solicitudes:
        if solicitud.ubicacion:
            point = to_shape(solicitud.ubicacion)
            solicitud.ubicacion = f"{point.y},{point.x}"
    
    return solicitudes


@router.delete("/{solicitud_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancelar_solicitud_servicio(
    solicitud_id: int,
    current_persona: Persona = Depends(get_current_persona),
    db: AsyncSession = Depends(get_db)
):
    """
    Cancela una solicitud de servicio (solo si está pendiente)
    """
    solicitud = await solicitud_servicio_crud.get(db, solicitud_id)
    if not solicitud:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    
    # Verificar que pertenece al usuario
    diagnostico = await diagnostico_crud.get(db, solicitud.id_diagnostico)
    solicitud_diag = await solicitud_diagnostico_crud.get(db, diagnostico.id_solicitud_diagnostico)
    
    if solicitud_diag.id_persona != current_persona.id:
        raise HTTPException(status_code=403, detail="No autorizado")
    
    # Solo se puede cancelar si está pendiente
    from app.models.solicitud_servicio import EstadoSolicitudServicio
    if solicitud.estado != EstadoSolicitudServicio.pendiente:
        raise HTTPException(
            status_code=400,
            detail="Solo se pueden cancelar solicitudes en estado pendiente"
        )
    
    await solicitud_servicio_crud.update_estado(
        db, solicitud_id, EstadoSolicitudServicio.cancelada
    )
    await db.commit()
    
    return None
