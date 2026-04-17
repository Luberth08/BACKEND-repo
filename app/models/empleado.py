from sqlalchemy import Column, Integer, ForeignKey, Enum, Date
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from datetime import date
import enum

class EstadoEmpleado(str, enum.Enum):
    activo = "activo"
    inactivo = "inactivo"
    ocupado = "ocupado"
    vacaciones = "vacaciones"

class Empleado(Base):
    __tablename__ = "empleado"

    id = Column(Integer, primary_key=True, index=True)
    fecha_ingreso = Column(Date, default=date.today)
    fecha_salida = Column(Date, nullable=True)
    estado = Column(Enum(EstadoEmpleado), nullable=False, default=EstadoEmpleado.activo)
    
    id_usuario = Column(Integer, ForeignKey("usuario.id", ondelete="RESTRICT"), nullable=False, unique=True)
    id_taller = Column(Integer, ForeignKey("taller.id", ondelete="CASCADE"), nullable=False)

    # Relaciones
    usuario = relationship("Usuario")
    taller = relationship("Taller")
    especialidades = relationship("TecnicoEspecialidad", back_populates="empleado", cascade="all, delete-orphan")
