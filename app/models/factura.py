from sqlalchemy import Column, Integer, String, DECIMAL, TIMESTAMP, ForeignKey, func, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.db.base_class import Base
import enum


class EstadoPago(str, enum.Enum):
    pendiente = "pendiente"
    pagado = "pagado"
    fallido = "fallido"
    reembolsado = "reembolsado"


class Factura(Base):
    __tablename__ = "factura"

    id = Column(Integer, primary_key=True, index=True)
    id_servicio = Column(
        Integer,
        ForeignKey("servicio.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    monto_total = Column(DECIMAL(10, 2), nullable=False)
    comision = Column(DECIMAL(10, 2), nullable=False)
    liquido_taller = Column(DECIMAL(10, 2), nullable=False)
    estado_pago = Column(SQLEnum(EstadoPago), nullable=False, default=EstadoPago.pendiente)
    
    # Datos para la pasarela o método de pago
    metodo_pago = Column(String(50), nullable=True) # "stripe", "efectivo", etc.
    id_pasarela = Column(String(255), nullable=True) # Stripe Session ID
    url_qr = Column(String(1000), nullable=True) # Checkout URL
    
    # Fechas
    fecha_emision = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    fecha_pago = Column(TIMESTAMP(timezone=True), nullable=True)

    # Relaciones
    servicio = relationship("Servicio", back_populates="facturas")
