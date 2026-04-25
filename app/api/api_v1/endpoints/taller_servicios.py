from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from geoalchemy2.shape import to_shape

from app.db.session import get_db
from app.core.deps import get_current_persona
from app.models.persona import Persona
from app.schemas.servicio import (
    SolicitudServicioListResponse,
    SolicitudServicioDetalleResponse,
    TecnicoDisponibleResponse,
    VehiculoTallerDisponibleResponse,
    ServicioCreate,
    ServicioResponse
)
from app.services import servicio_service
from app.crud import (
    solicitud_servicio as solicitud_servicio_crud,
    servicio as servicio_crud,
    rol_usuario as rol_usuario_crud,
    diagnostico as diagnostico_crud,
    solicitud_diagnostico as solicitud_diagnostico_crud,
    evidencia as evidencia_crud,
    vehiculo as vehiculo_crud
)

router = APIRouter(prefix="/taller", tags=["Taller - Gestión de Servicios"])


async def verificar_admin_taller(
    persona: Persona,
    db: AsyncSession
) -> int:
    """
    Verifica que la persona sea administrador de un taller y retorna el id_taller
    """
    # Obtener rol de administrador del usuario
    roles = await rol_usuario_crud.get_by_usuario(db, persona.id_usuario)
    
    for rol_usuario in roles:
        if rol_usuario.rol.nombre == "administrador" and rol_usuario.id_taller:
            return rol_usuario.id_taller
    
    raise HTTPException(
        status_code=403,
        detail="No tiene permisos de administrador de taller"
    )


@router.get("/solicitudes/recientes", response_model=List[SolicitudServicioListResponse])
async def obtener_solicitudes_recientes(
    current_persona: Persona = Depends(get_current_persona),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtiene solicitudes de servicio recientes (últimos 60 minutos) para el taller
    """
    id_taller = await verificar_admin_taller(current_persona, db)
    
    solicitudes = await servicio_service.obtener_solicitudes_recientes(
        db, id_taller, minutos=60
    )
    
    # Construir respuesta
    resultado = []
    for solicitud in solicitudes:
        # Verificar si ya tiene servicio creado
        servicio = await servicio_crud.get_by_solicitud(db, solicitud.id)
        
        resultado.append(SolicitudServicioListResponse(
            id=solicitud.id,
            fecha=solicitud.fecha,
            estado=solicitud.estado.value,
            sugerido_por=solicitud.sugerido_por.value,
            distancia_km=solicitud.distancia_km,
            comentario=solicitud.comentario,
            tiene_servicio=servicio is not None
        ))
    
    return resultado


@router.get("/solicitudes/historico", response_model=List[SolicitudServicioListResponse])
async def obtener_solicitudes_historico(
    current_persona: Persona = Depends(get_current_persona),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtiene todas las solicitudes de servicio (historial) para el taller
    """
    id_taller = await verificar_admin_taller(current_persona, db)
    
    solicitudes = await servicio_service.obtener_solicitudes_historicas(db, id_taller)
    
    # Construir respuesta
    resultado = []
    for solicitud in solicitudes:
        # Verificar si ya tiene servicio creado
        servicio = await servicio_crud.get_by_solicitud(db, solicitud.id)
        
        resultado.append(SolicitudServicioListResponse(
            id=solicitud.id,
            fecha=solicitud.fecha,
            estado=solicitud.estado.value,
            sugerido_por=solicitud.sugerido_por.value,
            distancia_km=solicitud.distancia_km,
            comentario=solicitud.comentario,
            tiene_servicio=servicio is not None
        ))
    
    return resultado


@router.get("/solicitudes/{solicitud_id}/detalle", response_model=SolicitudServicioDetalleResponse)
async def obtener_detalle_solicitud(
    solicitud_id: int,
    current_persona: Persona = Depends(get_current_persona),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtiene el detalle completo de una solicitud de servicio
    Incluye: fotos, audio, transcripción, diagnóstico, vehículo del cliente
    """
    id_taller = await verificar_admin_taller(current_persona, db)
    
    # Obtener solicitud
    solicitud = await solicitud_servicio_crud.get(db, solicitud_id)
    if not solicitud:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    
    if solicitud.id_taller != id_taller:
        raise HTTPException(
            status_code=403,
            detail="La solicitud no pertenece a su taller"
        )
    
    # Obtener diagnóstico
    diagnostico = await diagnostico_crud.get(db, solicitud.id_diagnostico)
    
    # Obtener solicitud de diagnóstico
    solicitud_diag = await solicitud_diagnostico_crud.get(db, diagnostico.id_solicitud_diagnostico)
    
    # Obtener evidencias
    evidencias = await evidencia_crud.get_by_solicitud_diagnostico(db, diagnostico.id_solicitud_diagnostico)
    
    # Obtener vehículo del cliente
    vehiculo = await vehiculo_crud.get(db, solicitud_diag.id_vehiculo)
    
    # Convertir ubicación a string
    ubicacion_str = None
    if solicitud.ubicacion:
        point = to_shape(solicitud.ubicacion)
        ubicacion_str = f"{point.y},{point.x}"
    
    # Construir respuesta
    from app.schemas.servicio import (
        EvidenciaDetalleResponse,
        VehiculoClienteResponse,
        DiagnosticoDetalleResponse
    )
    
    return SolicitudServicioDetalleResponse(
        id=solicitud.id,
        ubicacion=ubicacion_str,
        fecha=solicitud.fecha,
        comentario=solicitud.comentario,
        estado=solicitud.estado.value,
        sugerido_por=solicitud.sugerido_por.value,
        distancia_km=solicitud.distancia_km,
        diagnostico=DiagnosticoDetalleResponse(
            id=diagnostico.id,
            descripcion=diagnostico.descripcion,
            nivel_confianza=diagnostico.nivel_confianza,
            fecha=diagnostico.fecha
        ) if diagnostico else None,
        vehiculo_cliente=VehiculoClienteResponse(
            matricula=vehiculo.matricula,
            marca=vehiculo.marca,
            modelo=vehiculo.modelo,
            anio=vehiculo.anio,
            color=vehiculo.color,
            tipo=vehiculo.tipo
        ) if vehiculo else None,
        evidencias=[
            EvidenciaDetalleResponse(
                id=ev.id,
                url=ev.url,
                tipo=ev.tipo.value,
                transcripcion=ev.transcripcion
            ) for ev in evidencias
        ],
        descripcion_conductor=solicitud_diag.descripcion
    )


@router.get("/recursos/tecnicos-disponibles", response_model=List[TecnicoDisponibleResponse])
async def obtener_tecnicos_disponibles(
    current_persona: Persona = Depends(get_current_persona),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtiene la lista de técnicos disponibles del taller con sus especialidades
    """
    id_taller = await verificar_admin_taller(current_persona, db)
    
    tecnicos = await servicio_service.obtener_tecnicos_disponibles(db, id_taller)
    
    return [
        TecnicoDisponibleResponse(
            id=t['id'],
            nombre_completo=t['nombre_completo'],
            especialidades=t['especialidades'],
            estado=t['estado']
        ) for t in tecnicos
    ]


@router.get("/recursos/vehiculos-disponibles", response_model=List[VehiculoTallerDisponibleResponse])
async def obtener_vehiculos_disponibles(
    current_persona: Persona = Depends(get_current_persona),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtiene la lista de vehículos disponibles del taller
    """
    id_taller = await verificar_admin_taller(current_persona, db)
    
    vehiculos = await servicio_service.obtener_vehiculos_disponibles(db, id_taller)
    
    return [
        VehiculoTallerDisponibleResponse(
            id=v.id,
            matricula=v.matricula,
            marca=v.marca,
            modelo=v.modelo,
            tipo=v.tipo.value,
            estado=v.estado.value
        ) for v in vehiculos
    ]


@router.post("/solicitudes/{solicitud_id}/aceptar", response_model=ServicioResponse, status_code=status.HTTP_201_CREATED)
async def aceptar_solicitud(
    solicitud_id: int,
    servicio_data: ServicioCreate,
    current_persona: Persona = Depends(get_current_persona),
    db: AsyncSession = Depends(get_db)
):
    """
    Acepta una solicitud de servicio y crea un servicio asignando técnicos y vehículos
    """
    id_taller = await verificar_admin_taller(current_persona, db)
    
    try:
        servicio = await servicio_service.aceptar_solicitud_servicio(
            db=db,
            id_solicitud=solicitud_id,
            id_taller=id_taller,
            tecnicos_ids=servicio_data.tecnicos_ids,
            vehiculos_ids=servicio_data.vehiculos_ids
        )
        
        # Construir respuesta con técnicos y vehículos asignados
        from app.schemas.servicio import TecnicoAsignadoResponse, VehiculoAsignadoResponse
        from app.crud import empleado as empleado_crud
        from app.models.vehiculo_taller import VehiculoTaller
        from sqlalchemy import select
        
        # Obtener técnicos asignados
        tecnicos_response = []
        for tecnico_id in servicio_data.tecnicos_ids:
            empleado = await empleado_crud.get(db, tecnico_id)
            if empleado:
                tecnicos_response.append(TecnicoAsignadoResponse(
                    id_empleado=empleado.id,
                    nombre_completo=f"{empleado.nombre} {empleado.apellido}"
                ))
        
        # Obtener vehículos asignados
        vehiculos_response = []
        for vehiculo_id in servicio_data.vehiculos_ids:
            result = await db.execute(
                select(VehiculoTaller).where(VehiculoTaller.id == vehiculo_id)
            )
            vehiculo = result.scalar_one_or_none()
            if vehiculo:
                vehiculos_response.append(VehiculoAsignadoResponse(
                    id_vehiculo_taller=vehiculo.id,
                    matricula=vehiculo.matricula,
                    marca=vehiculo.marca,
                    modelo=vehiculo.modelo
                ))
        
        return ServicioResponse(
            id=servicio.id,
            fecha=servicio.fecha,
            estado=servicio.estado.value,
            id_taller=servicio.id_taller,
            id_solicitud_servicio=servicio.id_solicitud_servicio,
            tecnicos_asignados=tecnicos_response,
            vehiculos_asignados=vehiculos_response
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/solicitudes/{solicitud_id}/rechazar", status_code=status.HTTP_200_OK)
async def rechazar_solicitud(
    solicitud_id: int,
    current_persona: Persona = Depends(get_current_persona),
    db: AsyncSession = Depends(get_db)
):
    """
    Rechaza una solicitud de servicio
    """
    id_taller = await verificar_admin_taller(current_persona, db)
    
    try:
        solicitud = await servicio_service.rechazar_solicitud_servicio(
            db=db,
            id_solicitud=solicitud_id,
            id_taller=id_taller
        )
        
        return {
            "message": "Solicitud rechazada exitosamente",
            "solicitud_id": solicitud.id,
            "estado": solicitud.estado.value
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/servicios/en-proceso", response_model=List[ServicioResponse])
async def obtener_servicios_en_proceso(
    current_persona: Persona = Depends(get_current_persona),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtiene los servicios activos (creado, en_proceso) del taller
    """
    id_taller = await verificar_admin_taller(current_persona, db)
    
    servicios = await servicio_crud.get_en_proceso(db, id_taller)
    
    # Construir respuesta
    from app.schemas.servicio import TecnicoAsignadoResponse, VehiculoAsignadoResponse
    from app.crud import servicio_tecnico as servicio_tecnico_crud, servicio_vehiculo as servicio_vehiculo_crud
    from app.crud import empleado as empleado_crud
    from app.models.vehiculo_taller import VehiculoTaller
    from sqlalchemy import select
    
    resultado = []
    for servicio in servicios:
        # Obtener técnicos asignados
        tecnicos_asignados = await servicio_tecnico_crud.get_by_servicio(db, servicio.id)
        tecnicos_response = []
        for asignacion in tecnicos_asignados:
            empleado = await empleado_crud.get(db, asignacion.id_empleado)
            if empleado:
                tecnicos_response.append(TecnicoAsignadoResponse(
                    id_empleado=empleado.id,
                    nombre_completo=f"{empleado.nombre} {empleado.apellido}"
                ))
        
        # Obtener vehículos asignados
        vehiculos_asignados = await servicio_vehiculo_crud.get_by_servicio(db, servicio.id)
        vehiculos_response = []
        for asignacion in vehiculos_asignados:
            result = await db.execute(
                select(VehiculoTaller).where(VehiculoTaller.id == asignacion.id_vehiculo_taller)
            )
            vehiculo = result.scalar_one_or_none()
            if vehiculo:
                vehiculos_response.append(VehiculoAsignadoResponse(
                    id_vehiculo_taller=vehiculo.id,
                    matricula=vehiculo.matricula,
                    marca=vehiculo.marca,
                    modelo=vehiculo.modelo
                ))
        
        resultado.append(ServicioResponse(
            id=servicio.id,
            fecha=servicio.fecha,
            estado=servicio.estado.value,
            id_taller=servicio.id_taller,
            id_solicitud_servicio=servicio.id_solicitud_servicio,
            tecnicos_asignados=tecnicos_response,
            vehiculos_asignados=vehiculos_response
        ))
    
    return resultado


@router.get("/servicios/historico", response_model=List[ServicioResponse])
async def obtener_servicios_historico(
    current_persona: Persona = Depends(get_current_persona),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtiene los servicios completados o cancelados del taller
    """
    id_taller = await verificar_admin_taller(current_persona, db)
    
    servicios = await servicio_crud.get_historicos(db, id_taller)
    
    # Construir respuesta (mismo código que en-proceso)
    from app.schemas.servicio import TecnicoAsignadoResponse, VehiculoAsignadoResponse
    from app.crud import servicio_tecnico as servicio_tecnico_crud, servicio_vehiculo as servicio_vehiculo_crud
    from app.crud import empleado as empleado_crud
    from app.models.vehiculo_taller import VehiculoTaller
    from sqlalchemy import select
    
    resultado = []
    for servicio in servicios:
        # Obtener técnicos asignados
        tecnicos_asignados = await servicio_tecnico_crud.get_by_servicio(db, servicio.id)
        tecnicos_response = []
        for asignacion in tecnicos_asignados:
            empleado = await empleado_crud.get(db, asignacion.id_empleado)
            if empleado:
                tecnicos_response.append(TecnicoAsignadoResponse(
                    id_empleado=empleado.id,
                    nombre_completo=f"{empleado.nombre} {empleado.apellido}"
                ))
        
        # Obtener vehículos asignados
        vehiculos_asignados = await servicio_vehiculo_crud.get_by_servicio(db, servicio.id)
        vehiculos_response = []
        for asignacion in vehiculos_asignados:
            result = await db.execute(
                select(VehiculoTaller).where(VehiculoTaller.id == asignacion.id_vehiculo_taller)
            )
            vehiculo = result.scalar_one_or_none()
            if vehiculo:
                vehiculos_response.append(VehiculoAsignadoResponse(
                    id_vehiculo_taller=vehiculo.id,
                    matricula=vehiculo.matricula,
                    marca=vehiculo.marca,
                    modelo=vehiculo.modelo
                ))
        
        resultado.append(ServicioResponse(
            id=servicio.id,
            fecha=servicio.fecha,
            estado=servicio.estado.value,
            id_taller=servicio.id_taller,
            id_solicitud_servicio=servicio.id_solicitud_servicio,
            tecnicos_asignados=tecnicos_response,
            vehiculos_asignados=vehiculos_response
        ))
    
    return resultado


@router.post("/servicios/{servicio_id}/completar", status_code=status.HTTP_200_OK)
async def completar_servicio(
    servicio_id: int,
    current_persona: Persona = Depends(get_current_persona),
    db: AsyncSession = Depends(get_db)
):
    """
    Marca un servicio como completado y libera los recursos (técnicos y vehículos)
    """
    id_taller = await verificar_admin_taller(current_persona, db)
    
    try:
        servicio = await servicio_service.completar_servicio(
            db=db,
            id_servicio=servicio_id,
            id_taller=id_taller
        )
        
        return {
            "message": "Servicio completado exitosamente",
            "servicio_id": servicio.id,
            "estado": servicio.estado.value
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/servicios/{servicio_id}/detalle", response_model=ServicioResponse)
async def obtener_detalle_servicio(
    servicio_id: int,
    current_persona: Persona = Depends(get_current_persona),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtiene el detalle completo de un servicio
    """
    id_taller = await verificar_admin_taller(current_persona, db)
    
    servicio = await servicio_crud.get(db, servicio_id)
    if not servicio:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    
    if servicio.id_taller != id_taller:
        raise HTTPException(
            status_code=403,
            detail="El servicio no pertenece a su taller"
        )
    
    # Construir respuesta
    from app.schemas.servicio import TecnicoAsignadoResponse, VehiculoAsignadoResponse
    from app.crud import servicio_tecnico as servicio_tecnico_crud, servicio_vehiculo as servicio_vehiculo_crud
    from app.crud import empleado as empleado_crud
    from app.models.vehiculo_taller import VehiculoTaller
    from sqlalchemy import select
    
    # Obtener técnicos asignados
    tecnicos_asignados = await servicio_tecnico_crud.get_by_servicio(db, servicio.id)
    tecnicos_response = []
    for asignacion in tecnicos_asignados:
        empleado = await empleado_crud.get(db, asignacion.id_empleado)
        if empleado:
            tecnicos_response.append(TecnicoAsignadoResponse(
                id_empleado=empleado.id,
                nombre_completo=f"{empleado.nombre} {empleado.apellido}"
            ))
    
    # Obtener vehículos asignados
    vehiculos_asignados = await servicio_vehiculo_crud.get_by_servicio(db, servicio.id)
    vehiculos_response = []
    for asignacion in vehiculos_asignados:
        result = await db.execute(
            select(VehiculoTaller).where(VehiculoTaller.id == asignacion.id_vehiculo_taller)
        )
        vehiculo = result.scalar_one_or_none()
        if vehiculo:
            vehiculos_response.append(VehiculoAsignadoResponse(
                id_vehiculo_taller=vehiculo.id,
                matricula=vehiculo.matricula,
                marca=vehiculo.marca,
                modelo=vehiculo.modelo
            ))
    
    return ServicioResponse(
        id=servicio.id,
        fecha=servicio.fecha,
        estado=servicio.estado.value,
        id_taller=servicio.id_taller,
        id_solicitud_servicio=servicio.id_solicitud_servicio,
        tecnicos_asignados=tecnicos_response,
        vehiculos_asignados=vehiculos_response
    )
