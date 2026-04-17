from sqlalchemy import Column, Integer, Text, ForeignKey, DECIMAL, DateTime
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from datetime import datetime, timezone

class Diagnostico(Base):
    __tablename__ = "diagnostico"

    id = Column(Integer, primary_key=True, index=True)
    descripcion = Column(Text, nullable=False)
    nivel_confianza = Column(DECIMAL(5,4), nullable=True)
    fecha = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    id_solicitud = Column(Integer, ForeignKey("solicitud_diagnostico.id", ondelete="CASCADE"), nullable=False)

    # Relaciones
    solicitud = relationship("SolicitudDiagnostico", back_populates="diagnosticos")
