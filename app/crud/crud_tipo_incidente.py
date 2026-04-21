from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.crud.base import CRUDBase
from app.models.tipo_incidente import TipoIncidente


class CRUDTipoIncidente(CRUDBase[TipoIncidente]):
    async def get_by_concepto(self, db: AsyncSession, concepto: str) -> Optional[TipoIncidente]:
        result = await db.execute(select(TipoIncidente).where(TipoIncidente.concepto == concepto))
        return result.scalar_one_or_none()


tipo_incidente = CRUDTipoIncidente(TipoIncidente)
