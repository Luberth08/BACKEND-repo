from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from fastapi import HTTPException, status
from typing import List, Tuple
from app.crud.crud_categoria_incidente import categoria_incidente as crud_categoria
from app.crud.crud_tipo_incidente import tipo_incidente as crud_tipo
from app.schemas.categoria_incidente import (
    CategoriaIncidenteCreate,
    CategoriaIncidenteUpdate,
    CategoriaIncidenteResponse,
)


async def list_categorias(db: AsyncSession, skip: int = 0, limit: int = 10) -> Tuple[List[CategoriaIncidenteResponse], int]:
    total = await crud_categoria.count(db)
    items = await crud_categoria.get_all(db, skip=skip, limit=limit)
    resp = [CategoriaIncidenteResponse(id=i.id, nombre=i.nombre) for i in items]
    return resp, total


async def create_categoria(db: AsyncSession, data: CategoriaIncidenteCreate) -> CategoriaIncidenteResponse:
    existing = await crud_categoria.get_by_nombre(db, data.nombre)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Categoría con ese nombre ya existe")
    obj = await crud_categoria.create(db, data.dict())
    await db.commit()
    return CategoriaIncidenteResponse(id=obj.id, nombre=obj.nombre)


async def update_categoria(db: AsyncSession, id: int, data: CategoriaIncidenteUpdate) -> CategoriaIncidenteResponse:
    obj = await crud_categoria.get(db, id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoría no encontrada")
    if data.nombre and data.nombre != obj.nombre:
        other = await crud_categoria.get_by_nombre(db, data.nombre)
        if other:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Otra categoría ya usa ese nombre")
    update_data = {k: v for k, v in data.dict().items() if v is not None}
    updated = await crud_categoria.update(db, obj, update_data)
    await db.commit()
    return CategoriaIncidenteResponse(id=updated.id, nombre=updated.nombre)


async def delete_categoria(db: AsyncSession, id: int) -> None:
    # Verificar si existen tipos asociados
    stmt = select(func.count()).select_from(crud_tipo.model).where(crud_tipo.model.id_categoria_incidente == id)
    res = await db.execute(stmt)
    count = res.scalar_one()
    if count and count > 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No se puede eliminar: existen tipos de incidentes asociados")
    deleted = await crud_categoria.delete(db, id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoría no encontrada")
    await db.commit()
    return None
