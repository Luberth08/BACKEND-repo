from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.crud.crud_especialidad import especialidad as crud_especialidad
from app.schemas.especialidad import EspecialidadResponse

router = APIRouter(prefix="/especialidades", tags=["Especialidades"])

@router.get("/", response_model=list[EspecialidadResponse])
async def listar_especialidades(db: AsyncSession = Depends(get_db)):
    items = await crud_especialidad.get_all(db)
    return items