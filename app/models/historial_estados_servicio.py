from sqlalchemy import Column, Integer, Enum, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from app.models.servicio import EstadoServicio
from datetime import datetime, timezone

class HistorialEstadosServicio(Base):
    __tablename__ = "historial_estados_servicio"

    id = Column(Integer, primary_key=True, index=True)
    estado = Column(Enum(EstadoServicio), nullable=False)
    tiempo = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    id_servicio = Column(Integer, ForeignKey("servicio.id", ondelete="CASCADE"), nullable=False)

    # Relaciones
    servicio = relationship("Servicio", back_populates="historial_estados")
