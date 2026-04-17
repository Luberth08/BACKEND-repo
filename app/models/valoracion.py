from sqlalchemy import Column, Integer, Text, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Valoracion(Base):
    __tablename__ = "valoracion"

    id = Column(Integer, primary_key=True, index=True)
    puntos = Column(Integer, nullable=False)
    comentario = Column(Text, nullable=True)

    id_servicio = Column(Integer, ForeignKey("servicio.id", ondelete="CASCADE"), nullable=False, unique=True)

    # Relaciones
    servicio = relationship("Servicio")

    __table_args__ = (
        CheckConstraint('puntos >= 1 AND puntos <= 5', name='check_puntos_valoracion'),
    )
