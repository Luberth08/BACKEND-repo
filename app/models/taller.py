from sqlalchemy import Column, Integer, String, Boolean
from app.db.base_class import Base

class Taller(Base):
    __tablename__ = "taller"

    # atributos
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(200), nullable=False)
    ubicacion = Column(String(255))
    activo = Column(Boolean, default=False)
    # Puedes agregar más campos después