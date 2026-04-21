from pydantic import BaseModel
from typing import Optional

class TallerResponse(BaseModel):
    id: int
    nombre: str
    telefono: str
    email: str
    ubicacion: Optional[str] = None
    estado: str

    class Config:
        from_attributes = True