from pydantic import BaseModel
from typing import Optional

class EspecialidadBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None

class EspecialidadResponse(EspecialidadBase):
    id: int
    class Config:
        from_attributes = True