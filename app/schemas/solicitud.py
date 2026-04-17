from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
from enum import Enum

class EstadoSolicitudEnum(str, Enum):
    pendiente = "pendiente"
    aprobada = "aprobada"
    rechazada = "rechazada"

class SolicitudAfiliacionBase(BaseModel):
    nombre: str = Field(..., max_length=100)
    ubicacion: str  # GeoJSON? Podemos usar un string para lat,lon o un objeto
    telefono: str = Field(..., max_length=15)
    email: EmailStr
    comentario: Optional[str] = None

class SolicitudAfiliacionCreate(SolicitudAfiliacionBase):
    pass

class SolicitudAfiliacionResponse(SolicitudAfiliacionBase):
    id: int
    fecha: datetime
    fecha_revision: Optional[datetime]
    estado: EstadoSolicitudEnum
    id_usuario_solicita: int
    id_usuario_revisa: Optional[int]

    class Config:
        from_attributes = True

class SolicitudAfiliacionUpdateEstado(BaseModel):
    estado: EstadoSolicitudEnum
    comentario_revision: Optional[str] = None