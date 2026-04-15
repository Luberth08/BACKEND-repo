from app.crud.base import CRUDBase
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.taller import Taller
from sqlalchemy import select

class CRUDTaller(CRUDBase[Taller]):
    async def get_by_solicitud(self, db: AsyncSession, id_solicitud: int):
        result = await db.execute(select(Taller).where(Taller.id_solicitud_afiliacion == id_solicitud))
        return result.scalar_one_or_none()

taller = CRUDTaller(Taller)