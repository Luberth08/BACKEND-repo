from fastapi import Header, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.security import decode_access_token
from app.crud.crud_sesion import sesion as crud_sesion
from app.crud.crud_persona import persona as crud_persona
from app.models.persona import Persona

# Dependencia para obtener usuario actual desde token (para endpoints protegidos)
async def get_current_persona(
    token: str = Header(..., alias="Authorization"),
    db: AsyncSession = Depends(get_db)
) -> Persona:
    # El token viene como "Bearer <token>"
    if not token.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token format")
    token_value = token.split(" ")[1]
    
    payload = decode_access_token(token_value)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Buscar sesión activa
    sesion = await crud_sesion.get_by_token(db, token_value)
    if not sesion:
        raise HTTPException(status_code=401, detail="Session expired or invalid")
    
    persona = await crud_persona.get(db, sesion.id_persona)
    if not persona:
        raise HTTPException(status_code=401, detail="Persona not found")
    return persona