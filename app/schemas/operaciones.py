from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.solicitud_servicio import EstadoSolicitudServicio
from app.models.servicio import EstadoServicio
from app.schemas.emergencia import SolicitudDiagnosticoResponse

class SolicitudServicioResponse(BaseModel):
    id: int
    comentario: Optional[str]
    estado: EstadoSolicitudServicio
    costo_estimado: Optional[float]
    fecha: datetime
    id_solicitud_diagnostico: int
    solicitud_diagnostico: Optional[SolicitudDiagnosticoResponse] = None

    class Config:
        from_attributes = True

class AsignacionServicioCreate(BaseModel):
    id_empleados: List[int] = Field(..., description="IDs de los técnicos asignados")
    id_vehiculos_taller: List[int] = Field(..., description="IDs de los vehículos del taller (grúa, etc) a usar")
    costo_final: float = Field(..., description="Costo ofertado/final al cliente")

class ActualizarEstadoServicio(BaseModel):
    nuevo_estado: EstadoServicio = Field(...)

class HistorialEstadoResponse(BaseModel):
    estado: str
    tiempo: datetime

    class Config:
        from_attributes = True

class ServicioResponse(BaseModel):
    id: int
    fecha: datetime
    estado: EstadoServicio
    id_solicitud_servicio: int
    
    class Config:
        from_attributes = True
