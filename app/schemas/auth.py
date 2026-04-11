from pydantic import BaseModel, EmailStr, Field
from typing import Optional

# ---------- Request/Response para check-email ----------
class EmailCheckRequest(BaseModel):
    email: EmailStr

class EmailCheckResponse(BaseModel):
    exists: bool           # si la persona existe
    has_user: bool         # si la persona tiene un usuario asociado (con contraseña)

# ---------- Solicitar OTP ----------
class RequestOTPRequest(BaseModel):
    email: EmailStr

# ---------- Verificar OTP (para registro nuevo o login sin contraseña) ----------
class VerifyOTPRequest(BaseModel):
    email: EmailStr
    code: str = Field(..., min_length=6, max_length=6)
    fcm_token: Optional[str] = None

# ---------- Login con contraseña ----------
class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    fcm_token: Optional[str] = None

# ---------- Respuesta común ----------
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"





""" from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from app.schemas.persona import PersonaCreate

class EmailCheckRequest(BaseModel):
    email: EmailStr

class EmailCheckResponse(BaseModel):
    conductor_exists: bool
    user_exists: bool

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    fcm_token: Optional[str] = None

class RegisterConductorRequest(BaseModel):
    email: EmailStr
    persona: PersonaCreate
    fcm_token: Optional[str] = None

class CompleteRegistrationRequest(BaseModel):
    email: EmailStr
    code: str
    fcm_token: Optional[str] = None

class RegisterConductorFromUserRequest(BaseModel):
    email: EmailStr
    fcm_token: Optional[str] = None

class RequestOTPRequest(BaseModel):
    email: EmailStr

class LoginWithOTPRequest(BaseModel):
    email: EmailStr
    code: str
    fcm_token: Optional[str] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer" """