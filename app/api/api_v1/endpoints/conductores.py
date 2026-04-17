from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.conductor import CompleteProfileRequest
from app.schemas.auth import TokenResponse
from app.crud.crud_usuario import usuario as crud_usuario
from app.crud.crud_rol import rol as crud_rol
from app.crud.crud_rol_usuario import rol_usuario as crud_rol_usuario
from app.api.api_v1.deps import get_current_persona
from app.services.user_creation import create_usuario_from_persona, update_persona_data
from app.services.auth_utils import create_token_and_session
from app.models.persona import Persona

router = APIRouter(prefix="/conductores", tags=["Conductores"])

@router.post("/complete-profile", response_model=TokenResponse)
async def complete_profile(
    req: CompleteProfileRequest,
    current_persona: Persona = Depends(get_current_persona),
    db: AsyncSession = Depends(get_db)
):
    # Verificar que la persona no tenga ya un usuario
    existing_usuario = await crud_usuario.get_by_id_persona(db, current_persona.id)
    if existing_usuario:
        raise HTTPException(400, "User already exists for this person")
    # Asignar rol 'cliente'
    rol_cliente = await crud_rol.get_by_nombre(db, "cliente")
    if not rol_cliente:
        raise HTTPException(500, "Role 'cliente' not found")
    # Crear usuario
    nuevo_usuario = await create_usuario_from_persona(
        db, current_persona, req.username, req.password, req.url_img_perfil
    )
    # Asignar rol
    await crud_rol_usuario.add_rol(db, nuevo_usuario.id, rol_cliente.id)
    # Actualizar datos de persona (si se enviaron)
    persona_data = req.dict(exclude={"username", "password", "url_img_perfil"})
    if any(persona_data.values()):
        await update_persona_data(db, current_persona, persona_data)
    # Generar nuevo token (con roles actualizados)
    access_token = await create_token_and_session(db, current_persona.email)
    return TokenResponse(access_token=access_token)