from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.models.rol_usuario import RolUsuario

class CRUDRolUsuario:
    async def get_roles_by_usuario(self, db: AsyncSession, id_usuario: int) -> List[RolUsuario]:
        """Obtiene todas las relaciones rol-usuario para un usuario dado."""
        result = await db.execute(
            select(RolUsuario).where(RolUsuario.id_usuario == id_usuario)
        )
        return result.scalars().all()

    async def add_rol(self, db: AsyncSession, id_usuario: int, id_rol: int) -> RolUsuario:
        """Asigna un rol a un usuario."""
        nuevo = RolUsuario(id_usuario=id_usuario, id_rol=id_rol)
        db.add(nuevo)
        await db.commit()
        await db.refresh(nuevo)
        return nuevo

    async def remove_rol(self, db: AsyncSession, id_usuario: int, id_rol: int) -> None:
        """Elimina la asignación de un rol a un usuario."""
        await db.execute(
            delete(RolUsuario).where(
                RolUsuario.id_usuario == id_usuario,
                RolUsuario.id_rol == id_rol
            )
        )
        await db.commit()

    async def user_has_rol(self, db: AsyncSession, id_usuario: int, id_rol: int) -> bool:
        """Verifica si un usuario tiene un rol específico."""
        result = await db.execute(
            select(RolUsuario).where(
                RolUsuario.id_usuario == id_usuario,
                RolUsuario.id_rol == id_rol
            )
        )
        return result.scalar_one_or_none() is not None

rol_usuario = CRUDRolUsuario()