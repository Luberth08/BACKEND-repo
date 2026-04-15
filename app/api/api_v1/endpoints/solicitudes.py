from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from sqlalchemy import select
from app.schemas.solicitud import (
    SolicitudAfiliacionCreate, SolicitudAfiliacionResponse,
    SolicitudAfiliacionUpdateEstado
)
from app.crud.crud_solicitud_afiliacion import solicitud_afiliacion
from app.crud.crud_taller import taller as crud_taller
from app.crud.crud_rol import rol as crud_rol
from app.crud.crud_rol_usuario import rol_usuario as crud_rol_usuario
from app.api.api_v1.deps import get_current_usuario, require_permiso
from app.models.usuario import Usuario
from app.models.solicitud_afiliacion import EstadoSolicitudAfiliacion
from app.models.taller import Taller, EstadoTaller
from app.models.rol_usuario import RolUsuario
from geoalchemy2 import Geography
from geoalchemy2.shape import from_shape
from shapely.geometry import Point
from geoalchemy2.shape import to_shape
from datetime import datetime, timezone

router = APIRouter(prefix="/solicitudes", tags=["Afiliación de Talleres"])

def format_ubicacion(geog):
    """Convierte un objeto Geography a string 'lat,lon'."""
    if geog is None:
        return None
    point = to_shape(geog)
    return f"{point.y},{point.x}"  # lat,lon

@router.post("/afiliacion", response_model=SolicitudAfiliacionResponse, status_code=201)
async def crear_solicitud_afiliacion(
    req: SolicitudAfiliacionCreate,
    current_usuario: Usuario = Depends(require_permiso("solicitud:crear")),
    db: AsyncSession = Depends(get_db)
):
    # Convertir ubicación (string "lat,lon") a Geography
    try:
        lat, lon = map(float, req.ubicacion.split(','))
        point = Point(lon, lat)  # Note: lon, lat order
        ubicacion_geog = from_shape(point, srid=4326)
    except:
        raise HTTPException(400, "Ubicación inválida. Use formato 'lat,lon' (ej: -17.3895,-66.1568)")

    solicitud_data = req.dict(exclude={"ubicacion"})
    solicitud_data["ubicacion"] = ubicacion_geog
    solicitud_data["id_usuario_solicita"] = current_usuario.id
    solicitud = await solicitud_afiliacion.create(db, solicitud_data)
    response = SolicitudAfiliacionResponse(
        id=solicitud.id,
        nombre=solicitud.nombre,
        ubicacion=format_ubicacion(solicitud.ubicacion),
        telefono=solicitud.telefono,
        email=solicitud.email,
        comentario=solicitud.comentario,
        fecha=solicitud.fecha,
        fecha_revision=solicitud.fecha_revision,
        estado=solicitud.estado,
        id_usuario_solicita=solicitud.id_usuario_solicita,
        id_usuario_revisa=solicitud.id_usuario_revisa,
    )
    return response

@router.get("/afiliacion/mis-solicitudes", response_model=list[SolicitudAfiliacionResponse])
async def mis_solicitudes(
    current_usuario: Usuario = Depends(get_current_usuario),
    db: AsyncSession = Depends(get_db)
):
    solicitudes_db = await solicitud_afiliacion.get_by_usuario(db, current_usuario.id)
    # Convertir cada solicitud
    result = []
    for s in solicitudes_db:
        result.append(SolicitudAfiliacionResponse(
            id=s.id,
            nombre=s.nombre,
            ubicacion=format_ubicacion(s.ubicacion),
            telefono=s.telefono,
            email=s.email,
            comentario=s.comentario,
            fecha=s.fecha,
            fecha_revision=s.fecha_revision,
            estado=s.estado,
            id_usuario_solicita=s.id_usuario_solicita,
            id_usuario_revisa=s.id_usuario_revisa,
        ))
    return result

@router.get("/afiliacion/todas", response_model=list[SolicitudAfiliacionResponse])
async def todas_solicitudes(
    _: Usuario = Depends(require_permiso("solicitud:revisar")),
    db: AsyncSession = Depends(get_db)
):
    solicitudes = await solicitud_afiliacion.get_all(db)
    return solicitudes

@router.put("/afiliacion/{solicitud_id}/estado", response_model=SolicitudAfiliacionResponse)
async def revisar_solicitud(
    solicitud_id: int,
    req: SolicitudAfiliacionUpdateEstado,
    current_usuario: Usuario = Depends(require_permiso("solicitud:revisar")),
    db: AsyncSession = Depends(get_db)
):
    solicitud = await solicitud_afiliacion.get(db, solicitud_id)
    if not solicitud:
        raise HTTPException(404, "Solicitud no encontrada")
    if solicitud.estado != EstadoSolicitudAfiliacion.pendiente:
        raise HTTPException(400, "La solicitud ya fue procesada")
    
    solicitud.estado = req.estado
    solicitud.fecha_revision = datetime.now(timezone.utc)
    solicitud.id_usuario_revisa = current_usuario.id
    await db.commit()
    await db.refresh(solicitud)

    # Si se aprueba, crear taller y asignar rol super_admin_taller al solicitante
    if req.estado == EstadoSolicitudAfiliacion.aprobada:
        # Crear taller
        taller_data = {
            "nombre": solicitud.nombre,
            "ubicacion": solicitud.ubicacion,
            "telefono": solicitud.telefono,
            "email": solicitud.email,
            "hora_inicio": None,  # pendiente
            "hora_fin": None,
            "puntos": 0.0,
            "estado": EstadoTaller.activo,
            "id_solicitud_afiliacion": solicitud.id
        }
        nuevo_taller = await crud_taller.create(db, taller_data)
        
        # Asignar rol super_admin_taller al usuario solicitante
        rol_super_admin = await crud_rol.get_by_nombre(db, "super_admin_taller")
        if not rol_super_admin:
            raise HTTPException(500, "Rol 'super_admin_taller' no encontrado")
        # Verificar si ya tiene ese rol en ese taller (no debería)
        existing = await db.execute(
            select(RolUsuario).where(
                RolUsuario.id_usuario == solicitud.id_usuario_solicita,
                RolUsuario.id_rol == rol_super_admin.id,
                RolUsuario.id_taller == nuevo_taller.id
            )
        )
        if not existing.scalar_one_or_none():
            await crud_rol_usuario.add_rol(
                db, solicitud.id_usuario_solicita, rol_super_admin.id, id_taller=nuevo_taller.id
            )
    
    return solicitud