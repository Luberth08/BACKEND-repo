from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta
from app.core.config import settings
from app.core.security import verify_password, create_access_token
from app.db.session import get_db
from app.schemas.user import UserRegister, UserResponse
from app.schemas.token import Token
from app.crud.crud_persona import create_persona, get_persona_by_email
from app.crud.crud_usuario import create_usuario, get_usuario_by_email, get_usuario_by_username
from app.crud.crud_rol import get_rol_by_nombre, create_rol_if_not_exists
from app.crud.crud_rol_usuario import add_rol_to_user
from app.crud.crud_conductor import create_conductor
from app.api.api_v1.deps import get_current_user
from app.models.usuario import Usuario

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, db: AsyncSession = Depends(get_db)):
    # 1. Verificar si el email ya está registrado
    existing_persona = await get_persona_by_email(db, user_data.email)
    if existing_persona:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # 2. Verificar si el nombre de usuario ya existe
    existing_user = await get_usuario_by_username(db, user_data.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already taken")
    
    # 3. Crear persona
    persona_data = user_data.model_dump(exclude={"username", "password"})
    persona = await create_persona(db, persona_data)
    
    # 4. Crear usuario
    usuario = await create_usuario(db, nombre=user_data.username, contrasena=user_data.password, id_persona=persona.id)
    
    # 5. Asegurar que el rol 'cliente' existe
    rol_cliente = await get_rol_by_nombre(db, "cliente")
    if not rol_cliente:
        rol_cliente = await create_rol_if_not_exists(db, "cliente")
    
    # 6. Asignar rol 'cliente' al usuario
    await add_rol_to_user(db, id_usuario=usuario.id, id_rol=rol_cliente.id)
    
    # 7. Crear registro en tabla conductor (según tu diseño)
    await create_conductor(db, id_persona=persona.id)
    
    # 8. Preparar respuesta
    roles = ["cliente"]  # Podrías cargar desde la relación si tuviera más roles
    return UserResponse(
        id=usuario.id,
        nombre=usuario.nombre,
        email=persona.email,
        persona=persona,
        roles=roles
    )

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    # OAuth2PasswordRequestForm envía el "username", pero nosotros usamos email
    user = await get_usuario_by_email(db, email=form_data.username)
    if not user or not verify_password(form_data.password, user.contrasena):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.persona.email}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token)

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: Usuario = Depends(get_current_user)):
    # Obtener lista de roles del usuario
    roles = [rol_usuario.rol.nombre for rol_usuario in current_user.roles]
    return UserResponse(
        id=current_user.id,
        nombre=current_user.nombre,
        email=current_user.persona.email,
        persona=current_user.persona,
        roles=roles
    )