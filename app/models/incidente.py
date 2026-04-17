from sqlalchemy import Column, Integer, String, Enum, ForeignKey, DECIMAL, DateTime
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from datetime import datetime, timezone
import enum

class SugeridoPor(str, enum.Enum):
    ia = "ia"
    usuario = "usuario"
    admin = "admin"

class Incidente(Base):
    __tablename__ = "incidente"

    id = Column(Integer, primary_key=True, index=True)
    sugerido_por = Column(Enum(SugeridoPor), nullable=False, default=SugeridoPor.ia)
    nivel_confianza = Column(DECIMAL(5,4), nullable=True) # ej. 0.9520
    # No usamos server_default porque queremos que SQLAlchemy maneje esto como fallback en logic tier si no se manda 
    # pero mejor omitirlo o usar timezone.utc:
    fecha = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    id_tipo_incidente = Column(Integer, ForeignKey("tipo_incidente.id", ondelete="RESTRICT"), nullable=False)

    # Relaciones
    tipo_incidente = relationship("TipoIncidente")
