from typing import List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.taller import TallerResponse
from app.crud.crud_taller import taller as crud_taller
from geoalchemy2.shape import to_shape

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