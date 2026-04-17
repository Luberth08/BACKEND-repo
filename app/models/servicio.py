from sqlalchemy import Column, Integer, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from datetime import datetime, timezone
import enum

class EstadoServicio(str, enum.Enum):
    asignado = "asignado"
    en_camino = "en_camino"
    en_curso = "en_curso"
    finalizado = "finalizado"
    cancelado = "cancelado"

class Servicio(Base):
    __tablename__ = "servicio"

    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    estado = Column(Enum(EstadoServicio), nullable=False, default=EstadoServicio.asignado)
    
    id_solicitud_servicio = Column(Integer, ForeignKey("solicitud_servicio.id", ondelete="RESTRICT"), nullable=False, unique=True)

    # Relaciones
    solicitud_servicio = relationship("SolicitudServicio", backref="servicio")
    tecnicos = relationship("ServicioTecnico", back_populates="servicio", cascade="all, delete-orphan")
    vehiculos = relationship("ServicioVehiculo", back_populates="servicio", cascade="all, delete-orphan")
    historial_estados = relationship("HistorialEstadosServicio", back_populates="servicio", cascade="all, delete-orphan")
