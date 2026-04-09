from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.usuario import Usuario
from app.models.persona import Persona
from app.core.security import get_password_hash

async def create_usuario(db: AsyncSession, nombre: str, contrasena: str, id_persona: int) -> Usuario:
    hashed = get_password_hash(contrasena)
    db_obj = Usuario(nombre=nombre, contrasena=hashed, id_persona=id_persona)
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def get_usuario_by_email(db: AsyncSession, email: str) -> Usuario | None:
    result = await db.execute(
        select(Usuario).join(Persona).where(Persona.email == email)
    )
    return result.scalar_one_or_none()

async def get_usuario_by_username(db: AsyncSession, username: str) -> Usuario | None:
    result = await db.execute(select(Usuario).where(Usuario.nombre == username))
    return result.scalar_one_or_none()

async def get_usuario_by_id(db: AsyncSession, user_id: int) -> Usuario | None:
    result = await db.execute(select(Usuario).where(Usuario.id == user_id))
    return result.scalar_one_or_none()