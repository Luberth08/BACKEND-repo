from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class RolUsuario(Base):
    __tablename__ = "rol_usuario"

    # atributos
    id_usuario = Column(Integer, ForeignKey("usuario.id", ondelete="CASCADE"), primary_key=True)
    id_rol = Column(Integer, ForeignKey("rol.id", ondelete="RESTRICT"), primary_key=True)

    # relaciones
    usuario = relationship("Usuario", back_populates="roles")
    rol = relationship("Rol", back_populates="usuarios")