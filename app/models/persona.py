from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Persona(Base):
    __tablename__ = "persona"

    # atributos
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    apellido_p = Column(String(100), nullable=False)
    ci = Column(String(10), nullable=False)
    complemento = Column(String(2), nullable=True)
    telefono = Column(String(15), nullable=True)
    direccion = Column(String(255), nullable=True)
    email = Column(String(150), unique=True, nullable=False)

    # relaciones
    usuario = relationship("Usuario", back_populates="persona", uselist=False)
    conductor = relationship("Conductor", back_populates="persona", uselist=False)
    dispositivos = relationship("DispositivoUsuario", back_populates="persona")