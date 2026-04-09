from pydantic import BaseModel, EmailStr, Field
from app.schemas.persona import PersonaResponse

class UserRegister(BaseModel):
    # Datos de Persona
    nombre: str
    apellido_p: str
    ci: str
    complemento: str | None = None
    telefono: str | None = None
    direccion: str | None = None
    email: EmailStr
    
    # Datos de Usuario
    username: str = Field(..., alias="nombre_usuario")  # Nombre de usuario único
    password: str

    class Config:
        populate_by_name = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    nombre: str  # username
    email: str
    persona: PersonaResponse
    roles: list[str]

    class Config:
        from_attributes = True