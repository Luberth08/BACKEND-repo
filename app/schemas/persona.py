from pydantic import BaseModel, EmailStr

class PersonaBase(BaseModel):
    nombre: str
    apellido_p: str
    ci: str
    complemento: str | None = None
    telefono: str | None = None
    direccion: str | None = None
    email: EmailStr

class PersonaCreate(PersonaBase):
    pass

class PersonaResponse(PersonaBase):
    id: int

    class Config:
        from_attributes = True