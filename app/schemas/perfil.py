from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class UpdatePerfilRequest(BaseModel):
    username: Optional[str] = None
    url_img_perfil: Optional[str] = None
    nombre: Optional[str] = None
    apellido_p: Optional[str] = None
    apellido_m: Optional[str] = None
    ci: Optional[str] = None
    complemento: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None

class PerfilResponse(BaseModel):
    email: EmailStr
    username: Optional[str] = None
    url_img_perfil: Optional[str] = None
    nombre: Optional[str] = None
    apellido_p: Optional[str] = None
    apellido_m: Optional[str] = None
    ci: Optional[str] = None
    complemento: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None

class RequestPasswordChangeRequest(BaseModel):
    email: EmailStr

class ChangePasswordRequest(BaseModel):
    email: EmailStr
    code: str
    new_password: str = Field(..., min_length=6)