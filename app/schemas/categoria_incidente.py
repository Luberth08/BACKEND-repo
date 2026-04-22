from pydantic import BaseModel
from typing import List


class CategoriaIncidenteBase(BaseModel):
    nombre: str


class CategoriaIncidenteCreate(CategoriaIncidenteBase):
    pass


class CategoriaIncidenteUpdate(BaseModel):
    nombre: str | None = None


class CategoriaIncidenteResponse(CategoriaIncidenteBase):
    id: int

    class Config:
        from_attributes = True


class CategoriaIncidenteListResponse(BaseModel):
    items: List[CategoriaIncidenteResponse]
    total: int
    skip: int
    limit: int
