from sqlalchemy.ext.asyncio import AsyncSession
from app.models.rol_usuario import RolUsuario

async def add_rol_to_user(db: AsyncSession, id_usuario: int, id_rol: int, id_taller: int | None = None) -> RolUsuario:
    db_obj = RolUsuario(id_usuario=id_usuario, id_rol=id_rol, id_taller=id_taller)
    db.add(db_obj)
    await db.commit()
    return db_obj