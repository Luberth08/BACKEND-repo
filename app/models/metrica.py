from sqlalchemy import Column, Integer, DECIMAL, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class Metrica(Base):
    __tablename__ = "metrica"

    id = Column(Integer, primary_key=True, index=True)
    id_servicio = Column(
        Integer,
        ForeignKey("servicio.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,  # 1 metrica por servicio
        index=True
    )
    # Segundos desde creación de solicitud hasta aceptación del taller
    tiempo_respuesta = Column(DECIMAL(10, 2), nullable=True)
    # Segundos desde en_camino hasta en_lugar (tiempo de traslado real)
    tiempo_llegada = Column(DECIMAL(10, 2), nullable=True)
    # Segundos desde en_atencion hasta finalizado (tiempo de reparación)
    tiempo_resolucion = Column(DECIMAL(10, 2), nullable=True)

    # Relaciones
    servicio = relationship("Servicio", back_populates="metrica")
