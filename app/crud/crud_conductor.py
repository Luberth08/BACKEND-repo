from sqlalchemy.ext.asyncio import AsyncSession
from app.models.conductor import Conductor

async def create_conductor(db: AsyncSession, id_persona: int) -> Conductor:
    db_obj = Conductor(id_persona=id_persona)
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj