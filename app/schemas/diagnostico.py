from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class EvidenciaResponse(BaseModel):
    id: int
    url: str
    transcripcion: Optional[str] = None
    tipo: str

    class Config:
        orm_mode = True


class IncidenteResponse(BaseModel):
    id_tipo_incidente: int
    concepto: str
    nivel_confianza: float
    sugerido_por: str

    class Config:
        orm_mode = True


class DiagnosticoResponse(BaseModel):
    id: int
    descripcion: Optional[str]
    nivel_confianza: float
    fecha: datetime
    incidentes: List[IncidenteResponse] = []

    class Config:
        orm_mode = True


class SolicitudDiagnosticoResponse(BaseModel):
    id: int
    descripcion: Optional[str]
    fecha: datetime
    estado: str
    ubicacion: Optional[str]
    id_vehiculo: Optional[int]
    evidencias: List[EvidenciaResponse] = []
    diagnostico: Optional[DiagnosticoResponse] = None

    class Config:
        orm_mode = True
