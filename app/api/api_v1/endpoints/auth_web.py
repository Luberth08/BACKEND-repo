# app/api/api_v1/endpoints/auth_web.py
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.security import verify_password
from app.schemas.auth import LoginRequest, TokenResponse
from app.crud.crud_persona import persona as crud_persona
from app.crud.crud_usuario import usuario as crud_usuario
from app.crud.crud_sesion import sesion as crud_sesion
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