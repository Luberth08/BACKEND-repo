from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# ============================================================
# SCHEMAS PARA TÉCNICOS Y VEHÍCULOS
# ============================================================

class TecnicoDisponibleResponse(BaseModel):
    id: int
    nombre_completo: str
    especialidades: List[str] = []
    estado: str
    
    class Config:
        orm_mode = True


class VehiculoTallerDisponibleResponse(BaseModel):
    id: int
    matricula: str
    marca: str
    modelo: str
    tipo: str
    estado: str
    
    class Config:
        orm_mode = True


# ============================================================
# SCHEMAS PARA SERVICIO
# ============================================================

class TecnicoAsignadoResponse(BaseModel):
    id_empleado: int
    nombre_completo: str
    
    class Config:
        orm_mode = True


class VehiculoAsignadoResponse(BaseModel):
    id_vehiculo_taller: int
    matricula: str
    marca: str
    modelo: str
    
    class Config:
        orm_mode = True


class ServicioResponse(BaseModel):
    id: int
    fecha: datetime
    estado: str
    id_taller: int
    id_solicitud_servicio: Optional[int] = None
    tecnicos_asignados: List[TecnicoAsignadoResponse] = []
    vehiculos_asignados: List[VehiculoAsignadoResponse] = []
    
    class Config:
        orm_mode = True


class ServicioCreate(BaseModel):
    id_solicitud_servicio: int
    tecnicos_ids: List[int]
    vehiculos_ids: List[int]


# ============================================================
# SCHEMAS PARA SOLICITUDES (VISTA TALLER)
# ============================================================

class EvidenciaDetalleResponse(BaseModel):
    id: int
    url: str
    tipo: str
    transcripcion: Optional[str] = None
    
    class Config:
        orm_mode = True


class VehiculoClienteResponse(BaseModel):
    matricula: str
    marca: str
    modelo: str
    anio: int
    color: Optional[str] = None
    tipo: Optional[str] = None
    
    class Config:
        orm_mode = True


class DiagnosticoDetalleResponse(BaseModel):
    id: int
    descripcion: Optional[str] = None
    nivel_confianza: float
    fecha: datetime
    
    class Config:
        orm_mode = True


class SolicitudServicioDetalleResponse(BaseModel):
    """Schema completo para mostrar al administrador del taller"""
    id: int
    ubicacion: Optional[str] = None  # "lat,lon"
    fecha: datetime
    comentario: Optional[str] = None
    estado: str
    sugerido_por: str
    distancia_km: Optional[float] = None
    
    # Información del diagnóstico
    diagnostico: Optional[DiagnosticoDetalleResponse] = None
    
    # Información del vehículo del cliente
    vehiculo_cliente: Optional[VehiculoClienteResponse] = None
    
    # Evidencias (fotos, audio)
    evidencias: List[EvidenciaDetalleResponse] = []
    
    # Descripción del conductor
    descripcion_conductor: Optional[str] = None
    
    class Config:
        orm_mode = True


class SolicitudServicioListResponse(BaseModel):
    """Schema resumido para listar solicitudes"""
    id: int
    fecha: datetime
    estado: str
    sugerido_por: str
    distancia_km: Optional[float] = None
    comentario: Optional[str] = None
    tiene_servicio: bool = False
    
    class Config:
        orm_mode = True
