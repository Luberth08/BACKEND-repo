from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.db.base_class import Base
import enum

class TipoEvidencia(str, enum.Enum):
    audio = "audio"
    imagen = "imagen"
    texto = "texto"

class Evidencia(Base):
    __tablename__ = "evidencia"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(Text, nullable=True)
    transcripcion = Column(Text, nullable=True)
    tipo = Column(Enum(TipoEvidencia), nullable=False)
    id_solicitud = Column(Integer, ForeignKey("solicitud_diagnostico.id", ondelete="CASCADE"), nullable=False)

    # Relaciones
    solicitud = relationship("SolicitudDiagnostico", back_populates="evidencias")
