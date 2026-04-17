from sqlalchemy import Column, Integer, DECIMAL, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from datetime import datetime, timezone
import enum

class EstadoPago(str, enum.Enum):
    pendiente = "pendiente"
    pagado = "pagado"
    fallido = "fallido"

class Factura(Base):
    __tablename__ = "factura"

    id = Column(Integer, primary_key=True, index=True)
    monto_total = Column(DECIMAL(10,2), nullable=False)
    comision = Column(DECIMAL(10,2), nullable=False) # 10% del precio
    liquido_taller = Column(DECIMAL(10,2), nullable=False) # 90% del precio
    estado_pago = Column(Enum(EstadoPago), nullable=False, default=EstadoPago.pendiente)
    id_pasarela = Column(String(255), nullable=True)
    url_qr = Column(String(255), nullable=True)
    fecha_emision = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    fecha_pago = Column(DateTime(timezone=True), nullable=True)

    id_servicio = Column(Integer, ForeignKey("servicio.id", ondelete="RESTRICT"), nullable=False, unique=True)

    # Relaciones
    servicio = relationship("Servicio")
