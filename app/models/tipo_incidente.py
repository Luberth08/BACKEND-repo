from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.db.base_class import Base
import enum

class PrioridadIncidente(str, enum.Enum):
    baja = "baja"
    media = "media"
    alta = "alta"
    critica = "critica"
    emergencia = "emergencia"

class TipoIncidente(Base):
    __tablename__ = "tipo_incidente"

    id = Column(Integer, primary_key=True, index=True)
    concepto = Column(String(255), nullable=False)
    prioridad = Column(Enum(PrioridadIncidente), nullable=False, default=PrioridadIncidente.media)
    requiere_remolque = Column(Boolean, default=False)
    id_categoria_incidente = Column(Integer, ForeignKey("categoria_incidente.id", ondelete="RESTRICT"), nullable=False)

    # Relaciones
    categoria = relationship("CategoriaIncidente")
