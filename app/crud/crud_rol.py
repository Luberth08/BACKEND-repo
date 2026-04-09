from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.rol import Rol

async def get_rol_by_nombre(db: AsyncSession, nombre: str) -> Rol | None:
    result = await db.execute(select(Rol).where(Rol.nombre == nombre))
    return result.scalar_one_or_none()

async def create_rol_if_not_exists(db: AsyncSession, nombre: str) -> Rol:
    rol = await get_rol_by_nombre(db, nombre)
    if not rol:
        rol = Rol(nombre=nombre)
        db.add(rol)
        await db.commit()
        await db.refresh(rol)
    return rol