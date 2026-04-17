from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.crud.base import CRUDBase
from app.models.solicitud_afiliacion import SolicitudAfiliacion
from typing import Optional, List

class CRUDSolicitudAfiliacion(CRUDBase[SolicitudAfiliacion]):
    async def get_by_usuario(self, db: AsyncSession, id_usuario: int) -> List[SolicitudAfiliacion]:
        result = await db.execute(
            select(SolicitudAfiliacion).where(SolicitudAfiliacion.id_usuario_solicita == id_usuario)
        )
        return result.scalars().all()

    async def get_pendientes(self, db: AsyncSession) -> List[SolicitudAfiliacion]:
        result = await db.execute(
            select(SolicitudAfiliacion).where(SolicitudAfiliacion.estado == "pendiente")
        )
        return result.scalars().all()

solicitud_afiliacion = CRUDSolicitudAfiliacion(SolicitudAfiliacion)