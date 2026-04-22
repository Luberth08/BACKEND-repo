from typing import List, Tuple, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.schemas.taller import TallerResponse
from app.crud.crud_taller import taller as crud_taller
from geoalchemy2.shape import to_shape
from app.models.taller import EstadoTaller

def _format_ubicacion(geog) -> str:
    """Convierte un objeto Geography a string 'lat,lon'."""
    if geog is None:
        return ""
    point = to_shape(geog)
    return f"{point.y},{point.x}"

async def list_mis_talleres(
    db: AsyncSession,
    id_usuario: int,
    skip: int = 0,
    limit: int = 10
) -> Tuple[List[TallerResponse], int]:
    talleres, total = await crud_taller.get_by_usuario_admin(db, id_usuario, skip, limit)
    responses = []
    for t in talleres:
        responses.append(TallerResponse(
            id=t.id,
            nombre=t.nombre,
            telefono=t.telefono,
            email=t.email,
            ubicacion=_format_ubicacion(t.ubicacion),
            estado=t.estado
        ))
    return responses, total


async def list_all_talleres_admin(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 10,
    estado: Optional[str] = None
) -> Tuple[List[TallerResponse], int]:
    """Listado paginado para panel admin (todos los talleres), opcionalmente filtra por estado."""
    estado_enum: Optional[EstadoTaller] = None
    if estado:
        try:
            estado_enum = EstadoTaller(estado)
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Estado inválido")

    talleres, total = await crud_taller.get_paginated(db, skip=skip, limit=limit, estado=estado_enum)
    responses = []
    for t in talleres:
        responses.append(TallerResponse(
            id=t.id,
            nombre=t.nombre,
            telefono=t.telefono,
            email=t.email,
            ubicacion=_format_ubicacion(t.ubicacion),
            estado=t.estado.value if isinstance(t.estado, EstadoTaller) else str(t.estado)
        ))
    return responses, total


async def suspend_taller(db: AsyncSession, id_taller: int) -> TallerResponse:
    obj = await crud_taller.get(db, id_taller)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Taller no encontrado")
    if obj.estado == EstadoTaller.suspendido:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Taller ya está suspendido")
    updated = await crud_taller.update(db, obj, {"estado": EstadoTaller.suspendido})
    await db.commit()
    return TallerResponse(id=updated.id, nombre=updated.nombre, telefono=updated.telefono, email=updated.email, ubicacion=_format_ubicacion(updated.ubicacion), estado=updated.estado.value)


async def activar_taller(db: AsyncSession, id_taller: int) -> TallerResponse:
    obj = await crud_taller.get(db, id_taller)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Taller no encontrado")
    if obj.estado == EstadoTaller.activo:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Taller ya está activo")
    updated = await crud_taller.update(db, obj, {"estado": EstadoTaller.activo})
    await db.commit()
    return TallerResponse(id=updated.id, nombre=updated.nombre, telefono=updated.telefono, email=updated.email, ubicacion=_format_ubicacion(updated.ubicacion), estado=updated.estado.value)