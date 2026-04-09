from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Conductor(Base):
    __tablename__ = "conductor"

    id = Column(Integer, primary_key=True, index=True)
    id_persona = Column(Integer, ForeignKey("persona.id", ondelete="RESTRICT"), unique=True, nullable=False)

    persona = relationship("Persona", back_populates="conductor")