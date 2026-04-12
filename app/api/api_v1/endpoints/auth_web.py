# app/api/api_v1/endpoints/auth_web.py
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.security import get_password_hash
from app.core.security import verify_password
from app.schemas.auth import LoginRequest, TokenResponse, WebRegisterRequest
from app.crud.crud_persona import persona as crud_persona
from app.crud.crud_usuario import usuario as crud_usuario
from app.crud.crud_rol import rol as crud_rol
from app.crud.crud_rol_usuario import rol_usuario as crud_rol_usuario
from app.crud.crud_sesion import sesion as crud_sesion
from app.services.user_creation import create_persona_with_data
from app.services.auth_utils import create_token_and_session

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

@router.post("/register", response_model=TokenResponse)
async def web_register(
    req: WebRegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    rol_aspirante = await crud_rol.get_by_nombre(db, "aspirante")
    if not rol_aspirante:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Role 'aspirante' not found in database"
        )
    # Verificar que el username no exista
    existing_user = await crud_usuario.get_by_nombre(db, req.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    # Extraer datos opcionales de persona
    persona_extra = req.dict(exclude={"email", "password", "username"})
    # Crear persona 
    persona = await create_persona_with_data(db, req.email, persona_extra)
    # Crear usuario
    hashed = get_password_hash(req.password)
    usuario_data = {
        "nombre": req.username,
        "contrasena": hashed,
        "id_persona": persona.id
    }
    nuevo_usuario = await crud_usuario.create(db, usuario_data)
    # Asignar rol 'aspirante'
    await crud_rol_usuario.add_rol(db, nuevo_usuario.id, rol_aspirante.id)
    # Generar token y devolver
    access_token = await create_token_and_session(db, req.email)
    return TokenResponse(access_token=access_token)