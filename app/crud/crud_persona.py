from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.persona import Persona
from app.schemas.persona import PersonaCreate

async def create_persona(db: AsyncSession, obj_in: PersonaCreate) -> Persona:
    db_obj = Persona(**obj_in.model_dump())
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def get_persona_by_email(db: AsyncSession, email: str) -> Persona | None:
    result = await db.execute(select(Persona).where(Persona.email == email))
    return result.scalar_one_or_none()