from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.security import verify_password
from app.schemas.auth import (
    EmailCheckRequest, EmailCheckResponse,
    RequestOTPRequest, VerifyOTPRequest,
    LoginRequest, TokenResponse
)
from app.crud.crud_persona import persona as crud_persona
from app.crud.crud_usuario import usuario as crud_usuario
from app.crud.crud_sesion import sesion as crud_sesion
from app.services.otp_service import (
    generate_otp, store_otp, get_otp_data, delete_otp, send_otp_email
)
from app.api.api_v1.deps import require_mobile_platform
from app.models.persona import Persona
from app.services.auth_utils import create_token_and_session

router = APIRouter(prefix="/auth/mobile", tags=["Authentication - Mobile"])

# ========== FUNCIONES AUXILIARES ==========

async def _create_persona(db: AsyncSession, email: str) -> Persona:
    """Crea una nueva persona solo con email."""
    existing = await crud_persona.get_by_email(db, email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    persona_data = {"email": email}
    nueva_persona = await crud_persona.create(db, persona_data)
    return nueva_persona

async def _send_otp_email_safe(email: str, action: str, expires_minutes: int = 10) -> str:
    """
    Genera un OTP, lo envía por email y lo guarda en memoria con la acción especificada.
    """
    otp = generate_otp()
    store_otp(email, otp, expires_minutes=expires_minutes, temp_data={"action": action})
    send_otp_email(email, otp)
    return otp

# ========== ENDPOINTS ==========

@router.post("/check-email", response_model=EmailCheckResponse)
async def check_email(
    req: EmailCheckRequest,
    db: AsyncSession = Depends(get_db)
):
    """Verifica si el email existe y si tiene usuario asociado."""
    persona = await crud_persona.get_by_email(db, req.email)
    if not persona:
        return EmailCheckResponse(exists=False, has_user=False)
    usuario = await crud_usuario.get_by_id_persona(db, persona.id)
    return EmailCheckResponse(exists=True, has_user=usuario is not None)

@router.post("/request-otp", status_code=status.HTTP_200_OK)
async def request_otp(
    req: RequestOTPRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Solicita OTP para un email que ya existe (como persona) y NO tiene usuario.
    """
    persona = await crud_persona.get_by_email(db, req.email)
    if not persona:
        raise HTTPException(status_code=404, detail="Email not registered")
    usuario = await crud_usuario.get_by_id_persona(db, persona.id)
    if usuario:
        raise HTTPException(status_code=400, detail="User already has a password; use /login")
    await _send_otp_email_safe(req.email, action="verify")
    return {"message": "OTP sent"}

@router.post("/register", status_code=status.HTTP_200_OK)
async def register_new_conductor(
    req: RequestOTPRequest,  # solo email
    db: AsyncSession = Depends(get_db)
):
    """
    Email no existe. Se crea persona (solo email) y se envía OTP.
    """
    existing = await crud_persona.get_by_email(db, req.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    # Guardamos datos temporales de "registro"
    await _send_otp_email_safe(req.email, action="register")
    return {"message": "OTP sent. Please verify to complete registration."}

@router.post("/verify-otp", response_model=TokenResponse)
async def verify_otp(
    req: VerifyOTPRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Verifica OTP y realiza la acción correspondiente:
    - Si temp_data["action"] == "register": crea nueva persona y genera token.
    - Si temp_data["action"] == "verify": busca persona existente (sin usuario) y genera token.
    """
    record = get_otp_data(req.email)
    if not record or record["code"] != req.code:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")
    action = record["temp_data"].get("action")
    if action == "register":
        # Crear nueva persona
        persona = await _create_persona(db, req.email)
    elif action == "verify":
        # Persona debe existir y no tener usuario
        persona = await crud_persona.get_by_email(db, req.email)
        if not persona:
            raise HTTPException(status_code=404, detail="Persona not found")
        usuario = await crud_usuario.get_by_id_persona(db, persona.id)
        if usuario:
            raise HTTPException(status_code=400, detail="User already has a password; use /login")
    else:
        raise HTTPException(status_code=400, detail="Invalid OTP flow")
    # Generar token y sesión
    access_token = await create_token_and_session(db, req.email, fcm_token=req.fcm_token)
    delete_otp(req.email)
    return TokenResponse(access_token=access_token)

@router.post("/login", response_model=TokenResponse)
async def login_with_password(
    req: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Login con email y contraseña (para conductores con usuario, técnicos, admins).
    """
    # Buscar persona por email
    persona = await crud_persona.get_by_email(db, req.email)
    if not persona:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    # Buscar usuario asociado
    usuario = await crud_usuario.get_by_id_persona(db, persona.id)
    if not usuario:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    # Verificar contraseña
    if not verify_password(req.password, usuario.contrasena):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    # Generar token
    access_token = await create_token_and_session(db, req.email, fcm_token=req.fcm_token)
    return TokenResponse(access_token=access_token)

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Cierra la sesión actual (invalida el token).
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token")
    token_value = auth_header.split(" ")[1]
    sesion = await crud_sesion.get_by_token(db, token_value)
    if sesion and sesion.activa:
        sesion.activa = False
        await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)