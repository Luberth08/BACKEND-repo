from sqlalchemy import Column, Integer, String, DECIMAL, TIMESTAMP, ForeignKey, func
from sqlalchemy.orm import relationship
from app.db.base_class import Base
import enum
from sqlalchemy import Enum as SQLEnum


class EstadoHistorial(str, enum.Enum):
    creado = "creado"
    tecnico_asignado = "tecnico_asignado"
    en_camino = "en_camino"
    en_lugar = "en_lugar"
    en_atencion = "en_atencion"
    finalizado = "finalizado"
    cancelado = "cancelado"


class HistorialEstadosServicio(Base):
    __tablename__ = "historial_estados_servicio"

    id = Column(Integer, primary_key=True, index=True)
    id_servicio = Column(
        Integer,
        ForeignKey("servicio.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    estado = Column(SQLEnum(EstadoHistorial), nullable=False)
    fecha = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    # Tiempo en segundos desde el estado anterior (None para el primer estado)
    tiempo_desde_anterior = Column(DECIMAL(10, 2), nullable=True)

    # Relaciones
    servicio = relationship("Servicio", back_populates="historial_estados")
