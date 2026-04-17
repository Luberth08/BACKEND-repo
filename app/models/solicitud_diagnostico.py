from sqlalchemy import Column, Integer, Text, Enum, ForeignKey, DateTime
from geoalchemy2 import Geography
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from datetime import datetime, timezone
import enum

class EstadoSolicitudDiagnostico(str, enum.Enum):
    pendiente = "pendiente"
    procesando = "procesando"
    completado = "completado"
    fallido = "fallido"
    cancelado = "cancelado"

class SolicitudDiagnostico(Base):
    __tablename__ = "solicitud_diagnostico"

    id = Column(Integer, primary_key=True, index=True)
    descripcion = Column(Text, nullable=True)
    fecha = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    estado = Column(Enum(EstadoSolicitudDiagnostico), nullable=False, default=EstadoSolicitudDiagnostico.pendiente)
    ubicacion = Column(Geography(geometry_type='POINT', srid=4326), nullable=False)
    
    id_vehiculo = Column(Integer, ForeignKey("vehiculo.id", ondelete="RESTRICT"), nullable=False)
    id_incidente = Column(Integer, ForeignKey("incidente.id", ondelete="SET NULL"), nullable=True)

    # Relaciones
    vehiculo = relationship("Vehiculo")
    incidente = relationship("Incidente")
    evidencias = relationship("Evidencia", back_populates="solicitud", cascade="all, delete-orphan")
    diagnosticos = relationship("Diagnostico", back_populates="solicitud", cascade="all, delete-orphan")
