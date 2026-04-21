from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class CategoriaIncidente(Base):
    __tablename__ = "categoria_incidente"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False, unique=True)
    descripcion = Column(Text, nullable=True)

    tipos = relationship("TipoIncidente", back_populates="categoria")
