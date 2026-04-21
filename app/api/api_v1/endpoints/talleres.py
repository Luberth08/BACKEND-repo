from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.deps import get_current_usuario
from app.models.usuario import Usuario
from app.services import taller_service
from app.schemas.taller import TallerResponse

router = APIRouter(tags=["Talleres"])

@router.get("/mis-talleres", response_model=dict)
async def list_mis_talleres(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_usuario: Usuario = Depends(get_current_usuario),
    db: AsyncSession = Depends(get_db)
):
    items, total = await taller_service.list_mis_talleres(db, current_usuario.id, skip, limit)
    return {
        "items": items,
        "total": total,
        "skip": skip,
        "limit": limit
    }