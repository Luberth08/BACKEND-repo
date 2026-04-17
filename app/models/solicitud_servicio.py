from sqlalchemy import Column, Integer, Text, Enum, ForeignKey, DateTime, DECIMAL
from geoalchemy2 import Geography
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from datetime import datetime, timezone
import enum

class EstadoSolicitudServicio(str, enum.Enum):
    ofertada = "ofertada"
    aceptada = "aceptada"
    rechazada = "rechazada"

class SolicitudServicio(Base):
    __tablename__ = "solicitud_servicio"

    id = Column(Integer, primary_key=True, index=True)
    ubicacion = Column(Geography(geometry_type='POINT', srid=4326), nullable=False)
    fecha = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    comentario = Column(Text, nullable=True)
    estado = Column(Enum(EstadoSolicitudServicio), nullable=False, default=EstadoSolicitudServicio.ofertada)
    costo_estimado = Column(DECIMAL(10,2), nullable=True)
    
    id_taller = Column(Integer, ForeignKey("taller.id", ondelete="CASCADE"), nullable=False)
    id_solicitud_diagnostico = Column(Integer, ForeignKey("solicitud_diagnostico.id", ondelete="CASCADE"), nullable=False)

    # Relaciones
    taller = relationship("Taller")
    solicitud_diagnostico = relationship("SolicitudDiagnostico")
