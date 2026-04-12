from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum

class TipoVehiculoEnum(str, Enum):
    auto = "auto"
    camioneta = "camioneta"
    moto = "moto"
    camion = "camion"
    microbus = "microbus"
    otro = "otro"

class VehiculoBase(BaseModel):
    matricula: str = Field(..., max_length=20)
    marca: str = Field(..., max_length=100)
    modelo: str = Field(..., max_length=100)
    anio: int = Field(..., ge=1900, le=2100)
    color: Optional[str] = Field(None, max_length=50)
    tipo: TipoVehiculoEnum

class VehiculoCreate(VehiculoBase):
    pass

class VehiculoUpdate(BaseModel):
    matricula: Optional[str] = None
    marca: Optional[str] = None
    modelo: Optional[str] = None
    anio: Optional[int] = None
    color: Optional[str] = None
    tipo: Optional[TipoVehiculoEnum] = None

class VehiculoResponse(VehiculoBase):
    id: int

    class Config:
        from_attributes = True