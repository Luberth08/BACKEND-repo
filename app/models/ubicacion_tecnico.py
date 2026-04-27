from sqlalchemy import Column, Integer, DECIMAL, TIMESTAMP, ForeignKey, func, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class UbicacionTecnico(Base):
    __tablename__ = "ubicacion_tecnico"

    id = Column(Integer, primary_key=True, index=True)
    id_servicio = Column(
        Integer,
        ForeignKey("servicio.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    id_empleado = Column(
        Integer,
        ForeignKey("empleado.id", ondelete="CASCADE"),
        nullable=False
    )
    latitud = Column(DECIMAL(10, 7), nullable=False)
    longitud = Column(DECIMAL(10, 7), nullable=False)
    timestamp = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())

    # Relaciones
    servicio = relationship("Servicio", back_populates="ubicaciones_tecnicos")
    empleado = relationship("Empleado")

    # Garantiza un único registro por técnico+servicio (upsert lógico)
    __table_args__ = (
        UniqueConstraint('id_servicio', 'id_empleado', name='uq_ubicacion_tecnico_servicio'),
    )
