from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class DispositivoUsuario(Base):
    __tablename__ = "dispositivo_usuario"

    id = Column(Integer, primary_key=True, index=True)
    token_fcm = Column(String(500), nullable=False)
    id_persona = Column(Integer, ForeignKey("persona.id", ondelete="CASCADE"), nullable=False)

    persona = relationship("Persona", back_populates="dispositivos")