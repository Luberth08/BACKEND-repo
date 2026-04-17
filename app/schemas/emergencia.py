from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.evidencia import TipoEvidencia
from app.models.solicitud_diagnostico import EstadoSolicitudDiagnostico

class UbicacionBase(BaseModel):
    latitud: float
    longitud: float

class EvidenciaBase(BaseModel):
    tipo: TipoEvidencia
    url: Optional[str] = None
    transcripcion: Optional[str] = None

class EvidenciaCreate(EvidenciaBase):
    pass

class EvidenciaResponse(EvidenciaBase):
    id: int
    id_solicitud: int

    class Config:
        from_attributes = True

class SolicitudDiagnosticoBase(BaseModel):
    ubicacion: UbicacionBase
    descripcion: Optional[str] = None
    id_vehiculo: int

class SolicitudDiagnosticoCreate(SolicitudDiagnosticoBase):
    evidencias: Optional[List[EvidenciaCreate]] = []

class IncidenteResponse(BaseModel):
    id: int
    sugerido_por: str
    nivel_confianza: float
    fecha: datetime
    id_tipo_incidente: int

    class Config:
        from_attributes = True

class DiagnosticoResponse(BaseModel):
    id: int
    descripcion: str
    nivel_confianza: float
    fecha: datetime
    
    class Config:
        from_attributes = True

class SolicitudDiagnosticoResponse(BaseModel):
    id: int
    descripcion: Optional[str] = None
    id_vehiculo: int
    fecha: datetime
    estado: EstadoSolicitudDiagnostico
    id_incidente: Optional[int]
    incidente: Optional[IncidenteResponse]
    diagnosticos: List[DiagnosticoResponse] = []
    evidencias: List[EvidenciaResponse] = []

    class Config:
        from_attributes = True
