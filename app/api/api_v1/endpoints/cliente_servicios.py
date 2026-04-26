"""
Endpoints para clientes móvil - Seguimiento de servicios
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from app.db.session import get_db
from app.core.deps import get_current_usuario
from app.models.usuario import Usuario
from app.models.servicio import Servicio, EstadoServicio
from app.models.servicio_tecnico import ServicioTecnico
from app.models.solicitud_servicio import SolicitudServicio
from app.models.solicitud_diagnostico import SolicitudDiagnostico
from app.models.diagnostico import Diagnostico
from app.models.taller import Taller
from app.models.empleado import Empleado
from app.models.historial_estado_servicio import HistorialEstadoServicio
from app.crud import empleado as empleado_crud
from app.crud import crud_empleado_ubicacion
from app.schemas.servicio import (
    ServicioSeguimientoClienteResponse,
    TallerInfoResponse,
    TecnicoUbicacionResponse,
    EstadoHistorialClienteResponse
)
from geoalchemy2.shape import to_shape
from datetime import datetime

router = APIRouter(prefix="/cliente", tags=["Cliente - Seguimiento de Servicios"])


def get_estado_descripcion(estado: str) -> str:
    """Retorna la descripción en español del estado"""
    map_estados = {
        'creado': 'Creado',
        'tecnico_asignado': 'Técnico Asignado',
        'en_camino': 'En Camino',
        'en_lugar': 'En el Lugar',
        'en_atencion': 'En Atención',
        'finalizado': 'Finalizado',
        'cancelado': 'Cancelado'
    }
    return map_estados.get(estado, estado)


@router.get("/servicio-actual", response_model=Optional[ServicioSeguimientoClienteResponse])
async def obtener_servicio_actual(
    current_usuario: Usuario = Depends(get_current_usuario),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtiene el servicio actual en proceso del cliente con seguimiento completo:
    - Historial de estados
    - Ubicación de técnicos
    - Información del taller
    """
    # Buscar servicio activo del cliente
    # El cliente tiene servicios a través de solicitudes de diagnóstico
    result = await db.execute(
        select(Servicio).join(
            SolicitudServicio, Servicio.id_solicitud_servicio == SolicitudServicio.id
        ).join(
            Diagnostico, SolicitudServicio.id_diagnostico == Diagnostico.id
        ).join(
            SolicitudDiagnostico, Diagnostico.id_solicitud_diagnostico == SolicitudDiagnostico.id
        ).where(
            and_(
                SolicitudDiagnostico.id_persona == current_usuario.id_persona,
                Servicio.estado.in_([
                    EstadoServicio.creado,
                    EstadoServicio.tecnico_asignado,
                    EstadoServicio.en_camino,
                    EstadoServicio.en_lugar,
                    EstadoServicio.en_atencion
                ])
            )
        ).options(
            selectinload(Servicio.taller),
            selectinload(Servicio.solicitud_servicio).selectinload(SolicitudServicio.diagnostico)
        ).order_by(Servicio.fecha.desc())
    )
    
    servicio = result.scalar_one_or_none()
    
    if not servicio:
        return None
    
    # Obtener información del taller
    taller = servicio.taller
    taller_ubicacion = None
    if taller.ubicacion:
        point = to_shape(taller.ubicacion)
        taller_ubicacion = f"{point.y},{point.x}"
    
    taller_info = TallerInfoResponse(
        id=taller.id,
        nombre=taller.nombre,
        telefono=taller.telefono,
        email=taller.email,
        direccion=taller.direccion,
        ubicacion=taller_ubicacion,
        puntos=float(taller.puntos) if taller.puntos else 0.0
    )
    
    # Obtener técnicos asignados con sus ubicaciones
    result_tecnicos = await db.execute(
        select(ServicioTecnico).where(
            ServicioTecnico.id_servicio == servicio.id
        )
    )
    asignaciones = result_tecnicos.scalars().all()
    
    tecnicos_response = []
    for asignacion in asignaciones:
        empleado = await empleado_crud.get_with_usuario(db, asignacion.id_empleado)
        if empleado:
            # Obtener ubicación activa del técnico
            ubicacion = await crud_empleado_ubicacion.empleado_ubicacion.get_ubicacion_activa(
                db, empleado.id
            )
            
            tecnicos_response.append(TecnicoUbicacionResponse(
                id_empleado=empleado.id,
                nombre_completo=empleado.usuario.nombre,
                latitud=float(ubicacion.latitud) if ubicacion else None,
                longitud=float(ubicacion.longitud) if ubicacion else None,
                timestamp=ubicacion.timestamp if ubicacion else None,
                tiene_ubicacion=ubicacion is not None
            ))
    
    # Obtener historial de estados
    result_historial = await db.execute(
        select(HistorialEstadoServicio).where(
            HistorialEstadoServicio.id_servicio == servicio.id
        ).order_by(HistorialEstadoServicio.tiempo.asc())
    )
    historial = result_historial.scalars().all()
    
    historial_response = [
        EstadoHistorialClienteResponse(
            estado=h.estado.value,
            estado_descripcion=get_estado_descripcion(h.estado.value),
            tiempo=h.tiempo
        )
        for h in historial
    ]
    
    # Obtener ubicación del cliente (de la solicitud de diagnóstico)
    ubicacion_cliente = None
    if servicio.solicitud_servicio and servicio.solicitud_servicio.diagnostico:
        result_sol_diag = await db.execute(
            select(SolicitudDiagnostico).where(
                SolicitudDiagnostico.id == servicio.solicitud_servicio.diagnostico.id_solicitud_diagnostico
            )
        )
        sol_diag = result_sol_diag.scalar_one_or_none()
        if sol_diag and sol_diag.ubicacion:
            point = to_shape(sol_diag.ubicacion)
            ubicacion_cliente = f"{point.y},{point.x}"
    
    # Obtener descripción del diagnóstico
    diagnostico_descripcion = None
    if servicio.solicitud_servicio and servicio.solicitud_servicio.diagnostico:
        diagnostico_descripcion = servicio.solicitud_servicio.diagnostico.descripcion
    
    return ServicioSeguimientoClienteResponse(
        id=servicio.id,
        fecha=servicio.fecha,
        estado=servicio.estado.value,
        estado_descripcion=get_estado_descripcion(servicio.estado.value),
        taller=taller_info,
        tecnicos=tecnicos_response,
        historial_estados=historial_response,
        ubicacion_cliente=ubicacion_cliente,
        diagnostico_descripcion=diagnostico_descripcion
    )


@router.get("/servicio/{servicio_id}/tecnico/{empleado_id}/ruta")
async def obtener_ruta_tecnico(
    servicio_id: int,
    empleado_id: int,
    current_usuario: Usuario = Depends(get_current_usuario),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtiene la ruta optimizada desde la ubicación del técnico hasta el cliente.
    Usa OSRM para calcular la ruta.
    """
    # Verificar que el servicio pertenece al cliente
    result = await db.execute(
        select(Servicio).join(
            SolicitudServicio, Servicio.id_solicitud_servicio == SolicitudServicio.id
        ).join(
            Diagnostico, SolicitudServicio.id_diagnostico == Diagnostico.id
        ).join(
            SolicitudDiagnostico, Diagnostico.id_solicitud_diagnostico == SolicitudDiagnostico.id
        ).where(
            and_(
                Servicio.id == servicio_id,
                SolicitudDiagnostico.id_persona == current_usuario.id_persona
            )
        ).options(
            selectinload(Servicio.solicitud_servicio).selectinload(SolicitudServicio.diagnostico)
        )
    )
    
    servicio = result.scalar_one_or_none()
    if not servicio:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    
    # Verificar que el técnico está asignado al servicio
    result_asignacion = await db.execute(
        select(ServicioTecnico).where(
            and_(
                ServicioTecnico.id_servicio == servicio_id,
                ServicioTecnico.id_empleado == empleado_id
            )
        )
    )
    asignacion = result_asignacion.scalar_one_or_none()
    if not asignacion:
        raise HTTPException(status_code=404, detail="Técnico no asignado a este servicio")
    
    # Obtener ubicación del técnico
    ubicacion_tecnico = await crud_empleado_ubicacion.empleado_ubicacion.get_ubicacion_activa(
        db, empleado_id
    )
    
    if not ubicacion_tecnico:
        raise HTTPException(
            status_code=404,
            detail="El técnico no tiene ubicación disponible"
        )
    
    # Obtener ubicación del cliente
    result_sol_diag = await db.execute(
        select(SolicitudDiagnostico).where(
            SolicitudDiagnostico.id == servicio.solicitud_servicio.diagnostico.id_solicitud_diagnostico
        )
    )
    sol_diag = result_sol_diag.scalar_one_or_none()
    
    if not sol_diag or not sol_diag.ubicacion:
        raise HTTPException(status_code=404, detail="Ubicación del cliente no disponible")
    
    point_cliente = to_shape(sol_diag.ubicacion)
    
    # Calcular ruta usando OSRM
    import httpx
    
    lon_tecnico = float(ubicacion_tecnico.longitud)
    lat_tecnico = float(ubicacion_tecnico.latitud)
    lon_cliente = point_cliente.x
    lat_cliente = point_cliente.y
    
    osrm_url = f"http://router.project-osrm.org/route/v1/driving/{lon_tecnico},{lat_tecnico};{lon_cliente},{lat_cliente}"
    params = {
        "overview": "full",
        "geometries": "geojson"
    }
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(osrm_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get("code") != "Ok":
                raise HTTPException(status_code=500, detail="No se pudo calcular la ruta")
            
            route = data["routes"][0]
            geometry = route["geometry"]["coordinates"]
            distance = route["distance"]  # en metros
            duration = route["duration"]  # en segundos
            
            return {
                "ruta": geometry,  # Lista de [lon, lat]
                "distancia_metros": distance,
                "duracion_segundos": duration,
                "ubicacion_tecnico": {
                    "latitud": lat_tecnico,
                    "longitud": lon_tecnico
                },
                "ubicacion_cliente": {
                    "latitud": lat_cliente,
                    "longitud": lon_cliente
                }
            }
    
    except httpx.HTTPError:
        # Si falla OSRM, retornar línea recta
        return {
            "ruta": [[lon_tecnico, lat_tecnico], [lon_cliente, lat_cliente]],
            "distancia_metros": None,
            "duracion_segundos": None,
            "ubicacion_tecnico": {
                "latitud": lat_tecnico,
                "longitud": lon_tecnico
            },
            "ubicacion_cliente": {
                "latitud": lat_cliente,
                "longitud": lon_cliente
            },
            "fallback": True
        }
