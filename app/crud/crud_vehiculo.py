from app.crud.base import CRUDBase
from app.models.vehiculo import Vehiculo
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

class CRUDVehiculo(CRUDBase[Vehiculo]):
    async def get_by_persona(self, db: AsyncSession, id_persona: int):
        result = await db.execute(select(Vehiculo).where(Vehiculo.id_persona == id_persona))
        return result.scalars().all()

vehiculo = CRUDVehiculo(Vehiculo)