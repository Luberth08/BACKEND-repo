from sqlalchemy import Column, Integer, String, SmallInteger, Enum, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from app.models.vehiculo import TipoVehiculo
import enum

class EstadoVehiculoTaller(str, enum.Enum):
    disponible = "disponible"
    en_servicio = "en_servicio"
    mantenimiento = "mantenimiento"
    inactivo = "inactivo"

class VehiculoTaller(Base):
    __tablename__ = "vehiculo_taller"

    id = Column(Integer, primary_key=True, index=True)
    matricula = Column(String(20), nullable=False, unique=True)
    marca = Column(String(100), nullable=False)
    modelo = Column(String(100), nullable=False)
    anio = Column(SmallInteger, nullable=False)
    color = Column(String(50), nullable=True)
    tipo = Column(Enum(TipoVehiculo), nullable=False)
    estado = Column(Enum(EstadoVehiculoTaller), nullable=False, default=EstadoVehiculoTaller.disponible)
    
    id_taller = Column(Integer, ForeignKey("taller.id", ondelete="CASCADE"), nullable=False)

    # Relaciones
    taller = relationship("Taller")

    # restricciones
    __table_args__ = (
        CheckConstraint('anio >= 1900 AND anio <= 2100', name='check_anio_vehiculo_taller'),
    )
