from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.perfil import UpdatePerfilRequest, PerfilResponse, RequestPasswordChangeRequest, ChangePasswordRequest
from app.crud.crud_persona import persona as crud_persona
from app.crud.crud_usuario import usuario as crud_usuario
from app.crud.crud_sesion import sesion as crud_sesion
from app.api.api_v1.deps import get_current_persona
from app.models.persona import Persona
from app.services.user_creation import update_persona_data
from app.services.otp_service import get_otp_data, delete_otp, send_otp_email_safe
from app.core.security import get_password_hash 
from typing import Optional

router = APIRouter(prefix="/perfil", tags=["Perfil"])

@router.put("/me", response_model=PerfilResponse)
async def update_my_profile(
    req: UpdatePerfilRequest,
    current_persona: Persona = Depends(get_current_persona),
    db: AsyncSession = Depends(get_db)
):
    """
    Actualiza la informacion del usuario
    """
    # Verificar si el usuario tiene cuenta (usuario)
    usuario = await crud_usuario.get_by_id_persona(db, current_persona.id)
    # Validar y actualizar username
    if req.username is not None:
        if not usuario:
            raise HTTPException(
                status_code=400,
                detail="No se puede cambiar el nombre de usuario porque no tienes una cuenta con contraseña. Crea una cuenta primero."
            )
        # Verificar que el nuevo username no esté en uso por otro usuario
        if req.username != usuario.nombre:
            existing = await crud_usuario.get_by_nombre(db, req.username)
            if existing and existing.id != usuario.id:
                raise HTTPException(400, "El nombre de usuario ya está en uso")
            # Actualizar username
            usuario.nombre = req.username
            db.add(usuario)
    # Actualizar foto de perfil (si se envía)
    if req.url_img_perfil is not None and usuario:
        usuario.url_img_perfil = req.url_img_perfil
        db.add(usuario)
    # Actualizar datos de persona (solo los campos no nulos)
    persona_update = {}
    for field in ["nombre", "apellido_p", "apellido_m", "ci", "complemento", "telefono", "direccion"]:
        value = getattr(req, field, None)
        if value is not None:
            persona_update[field] = value
    # Validar CI único si se está actualizando
    if "ci" in persona_update:
        ci = persona_update["ci"]
        complemento = persona_update.get("complemento")
        existing_persona = await crud_persona.get_by_ci_complemento(db, ci, complemento)
        if existing_persona and existing_persona.id != current_persona.id:
            raise HTTPException(400, "Ya existe una persona con ese CI")
    if persona_update:
        current_persona = await update_persona_data(db, current_persona, persona_update)
    # Guardar cambios (commit)
    await db.commit()
    await db.refresh(current_persona)
    if usuario:
        await db.refresh(usuario)
    # Construir respuesta
    return PerfilResponse(
        email=current_persona.email,
        username=usuario.nombre if usuario else None,
        url_img_perfil=usuario.url_img_perfil if usuario else None,
        nombre=current_persona.nombre,
        apellido_p=current_persona.apellido_p,
        apellido_m=current_persona.apellido_m,
        ci=current_persona.ci,
        complemento=current_persona.complemento,
        telefono=current_persona.telefono,
        direccion=current_persona.direccion,
    )

@router.post("/request-password-change", status_code=200)
async def request_password_change(
    req: RequestPasswordChangeRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Envía un OTP al email del usuario para iniciar el proceso de cambio de contraseña.
    """
    # Verificar que el email exista en persona y tenga usuario asociado
    persona = await crud_persona.get_by_email(db, req.email)
    if not persona:
        raise HTTPException(404, "Email not registered")
    usuario = await crud_usuario.get_by_id_persona(db, persona.id)
    if not usuario:
        raise HTTPException(400, "This email does not have a password (no user account).")
    
    # Generar OTP y guardar con acción "password_change"
    await send_otp_email_safe(req.email, action="password_change")
    return {"message": "OTP sent to your email"}

@router.post("/change-password", status_code=200)
async def change_password(
    req: ChangePasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    # Obtener datos OTP
    record = get_otp_data(req.email)
    if not record or record["code"] != req.code:
        raise HTTPException(400, "Invalid or expired OTP")
    if record["temp_data"].get("action") != "password_change":
        raise HTTPException(400, "Invalid OTP flow")
    # Buscar persona y usuario
    persona = await crud_persona.get_by_email(db, req.email)
    if not persona:
        raise HTTPException(404, "Persona not found")
    usuario = await crud_usuario.get_by_id_persona(db, persona.id)
    if not usuario:
        raise HTTPException(400, "User account not found")
    # Actualizar contraseña
    hashed = get_password_hash(req.new_password)
    usuario.contrasena = hashed
    db.add(usuario)
    await db.commit()
    # Invalidar OTP y opcionalmente todas las sesiones del usuario (por seguridad)
    delete_otp(req.email)
    # Podrías invalidar todas las sesiones de esta persona para que tenga que volver a iniciar sesión
    await crud_sesion.invalidate_all_for_persona(db, persona.id)
    return {"message": "Password changed successfully. Please log in again."}