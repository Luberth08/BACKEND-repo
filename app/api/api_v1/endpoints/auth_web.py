# app/api/api_v1/endpoints/auth_web.py
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.security import get_password_hash
from app.core.security import verify_password
from app.schemas.auth import LoginRequest, TokenResponse, WebRegisterRequest, RegisterInitRequest, RegisterCompleteRequest
from app.crud.crud_persona import persona as crud_persona
from app.crud.crud_usuario import usuario as crud_usuario
from app.crud.crud_rol import rol as crud_rol
from app.crud.crud_rol_usuario import rol_usuario as crud_rol_usuario
from app.crud.crud_sesion import sesion as crud_sesion
from app.services.user_creation import create_persona_with_data
from app.services.auth_utils import create_token_and_session
from app.services.otp_service import (
    get_otp_data, delete_otp, send_otp_email_safe
)

router = APIRouter(prefix="/auth/web", tags=["Authentication - Web"])

@router.post("/login", response_model=TokenResponse)
async def web_login(
    req: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    persona = await crud_persona.get_by_email(db, req.email)
    if not persona:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    usuario = await crud_usuario.get_by_id_persona(db, persona.id)
    if not usuario:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not verify_password(req.password, usuario.contrasena):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = await create_token_and_session(db, req.email)
    return TokenResponse(access_token=access_token)

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def web_logout(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token")
    token_value = auth_header.split(" ")[1]
    sesion = await crud_sesion.get_by_token(db, token_value)
    if sesion and sesion.activa:
        sesion.activa = False
        await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.post("/register/init", status_code=200)
async def register_init(
    req: RegisterInitRequest,
    db: AsyncSession = Depends(get_db)
):
    # Verificar si el email ya existe en persona
    existing_persona = await crud_persona.get_by_email(db, req.email)
    persona_exists = existing_persona is not None
    user_exists = False
    if persona_exists:
        # Verificar si esa persona ya tiene usuario asociado
        usuario = await crud_usuario.get_by_id_persona(db, existing_persona.id)
        user_exists = usuario is not None
        if user_exists:
            raise HTTPException(400, "Email already registered as a user")
    # Validar que el username no exista en usuario
    existing_user = await crud_usuario.get_by_nombre(db, req.username)
    if existing_user:
        raise HTTPException(400, "Username already taken")
    # Validar CI único (si se proporciona)
    if req.ci:
        existing_ci = await crud_persona.get_by_ci_complemento(db, req.ci, req.complemento)
        if existing_ci:
            raise HTTPException(400, "CI already registered")
    # Guardar datos temporalmente y enviar OTP
    temp_data = {
        "data": req.dict(),
        "persona_exists": persona_exists,
        "id_persona": existing_persona.id if persona_exists else None
    }
    await send_otp_email_safe(req.email, action="register", extra_temp_data=temp_data)
    return {"message": "OTP sent to your email"}

@router.post("/register/complete", response_model=TokenResponse)
async def register_complete(
    req: RegisterCompleteRequest,
    db: AsyncSession = Depends(get_db)
):    
    # Verificar OTP
    record = get_otp_data(req.email)
    if not record or record["code"] != req.code:
        raise HTTPException(400, "Invalid or expired OTP")
    temp_data = record["temp_data"]
    if temp_data.get("action") != "register":
        raise HTTPException(400, "Invalid OTP flow")
    # Verificar que existe rol
    rol_aspirante = await crud_rol.get_by_nombre(db, "aspirante")
    if not rol_aspirante:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Role 'aspirante' not found in database"
        )
    # Recuperar datos
    user_data = temp_data["data"]
    persona_exists = temp_data.get("persona_exists", False)
    id_persona = temp_data.get("id_persona")
    existing_user = await crud_usuario.get_by_nombre(db, user_data["username"])
    if existing_user:
        raise HTTPException(400, "Username already taken")
    # Obtener o crear persona
    if persona_exists and id_persona:
        persona = await crud_persona.get(db, id_persona)
        if not persona:
            raise HTTPException(400, "Persona not found")
    else:
        # Crear nueva persona con los datos opcionales
        persona_extra = {k: v for k, v in user_data.items() if k not in ["email", "username", "password"]}
        persona = await create_persona_with_data(db, user_data["email"], persona_extra)
    
    # Crear usuario
    hashed = get_password_hash(user_data["password"])
    usuario_data = {
        "nombre": user_data["username"],
        "contrasena": hashed,
        "id_persona": persona.id
    }
    nuevo_usuario = await crud_usuario.create(db, usuario_data)
    # Asignar rol 'aspirante'
    await crud_rol_usuario.add_rol(db, nuevo_usuario.id, rol_aspirante.id)
    # Generar token
    access_token = await create_token_and_session(db, user_data["email"])
    # Limpiar OTP
    delete_otp(req.email)
    return TokenResponse(access_token=access_token)