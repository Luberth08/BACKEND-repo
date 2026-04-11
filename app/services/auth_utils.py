from datetime import datetime, timedelta, timezone
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.core.config import settings
from app.core.security import create_access_token
from app.crud.crud_persona import persona as crud_persona
from app.crud.crud_usuario import usuario as crud_usuario
from app.crud.crud_rol_usuario import rol_usuario as crud_rol_usuario
from app.crud.crud_sesion import sesion as crud_sesion
from app.crud.crud_dispositivo_usuario import dispositivo_usuario as crud_dispositivo

async def _save_fcm_token(db: AsyncSession, persona_id: int, fcm_token: Optional[str]):
    """Guarda el token FCM si es nuevo."""
    if fcm_token:
        dispositivos = await crud_dispositivo.get_by_persona(db, persona_id)
        if not any(d.token_fcm == fcm_token for d in dispositivos):
            await crud_dispositivo.create(db, {"token_fcm": fcm_token, "id_persona": persona_id})

async def create_token_and_session(
    db: AsyncSession,
    email: str,
    fcm_token: Optional[str] = None
) -> str:
    """Genera token JWT, guarda sesión y retorna token."""
    # Buscar persona por email
    persona = await crud_persona.get_by_email(db, email)
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")
    # Buscar usuario asociado
    usuario = await crud_usuario.get_by_id_persona(db, persona.id)
    # Determinar roles
    if usuario:
        roles = await crud_rol_usuario.get_roles_by_usuario(db, usuario.id)
        role_names = [r.rol.nombre for r in roles]
    else:
        # Conductor sin usuario
        role_names = ["conductor"]
    # Construir payload del token
    expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    data = {
        "sub": email,
        "persona_id": persona.id,
        "roles": role_names,
    }
    access_token = create_access_token(data, expires_delta=expires_delta)
    # Guardar sesión
    expires_at = datetime.now(timezone.utc) + expires_delta
    await crud_sesion.create_session(db, access_token, expires_at, persona.id)
    # Guardar FCM token si se proporcionó
    if fcm_token:
        await _save_fcm_token(db, persona.id, fcm_token)
    return access_token