from sqlalchemy import Column, Integer, ForeignKey, TIMESTAMP, func
from sqlalchemy.orm import relationship
from app.db.base_class import Base
import enum
from sqlalchemy import Enum as SQLEnum


class EstadoServicio(str, enum.Enum):
    creado = "creado"
    tecnico_asignado = "tecnico_asignado"
    en_camino = "en_camino"
    en_lugar = "en_lugar"
    en_atencion = "en_atencion"
    finalizado = "finalizado"
    cancelado = "cancelado"


class Servicio(Base):
    __tablename__ = "servicio"

    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    estado = Column(SQLEnum(EstadoServicio), nullable=False, default=EstadoServicio.creado)
    id_taller = Column(Integer, ForeignKey("taller.id", ondelete="RESTRICT"), nullable=False)
    id_solicitud_servicio = Column(
        Integer, 
        ForeignKey("solicitud_servicio.id", ondelete="SET NULL"), 
        nullable=True,
        unique=True
    )

    # Relaciones
    taller = relationship("Taller", back_populates="servicios")
    solicitud_servicio = relationship("SolicitudServicio", back_populates="servicio")
    tecnicos_asignados = relationship("ServicioTecnico", back_populates="servicio", cascade="all, delete-orphan")
    vehiculos_asignados = relationship("ServicioVehiculo", back_populates="servicio", cascade="all, delete-orphan")
    # CU-13 / CU-14 / CU-15
    historial_estados = relationship("HistorialEstadosServicio", back_populates="servicio", cascade="all, delete-orphan", order_by="HistorialEstadosServicio.fecha")
    metrica = relationship("Metrica", back_populates="servicio", uselist=False, cascade="all, delete-orphan")
    mensajes = relationship("Mensaje", back_populates="servicio", cascade="all, delete-orphan", order_by="Mensaje.tiempo")
    ubicaciones_tecnicos = relationship("UbicacionTecnico", back_populates="servicio", cascade="all, delete-orphan")
    facturas = relationship("Factura", back_populates="servicio", cascade="all, delete-orphan")
