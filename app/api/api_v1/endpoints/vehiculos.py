from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.vehiculo import VehiculoCreate, VehiculoUpdate, VehiculoResponse
from app.crud.crud_vehiculo import vehiculo as crud_vehiculo
from app.api.api_v1.deps import get_current_persona, require_permiso
from app.models.persona import Persona
from sqlalchemy import select
from app.models.vehiculo import Vehiculo

router = APIRouter(prefix="/vehiculos", tags=["Vehículos"])

@router.get("/", response_model=list[VehiculoResponse])
async def list_vehiculos(
    current_persona: Persona = Depends(get_current_persona),
    db: AsyncSession = Depends(get_db)
):
    vehiculos = await crud_vehiculo.get_by_persona(db, current_persona.id)
    return vehiculos

@router.get("/{vehiculo_id}", response_model=VehiculoResponse)
async def get_vehiculo(
    vehiculo_id: int,
    current_persona: Persona = Depends(get_current_persona),
    db: AsyncSession = Depends(get_db)
):
    vehiculo = await crud_vehiculo.get(db, vehiculo_id)
    if not vehiculo or vehiculo.id_persona != current_persona.id:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    return vehiculo

@router.post("/", response_model=VehiculoResponse, status_code=201)
async def create_vehiculo(
    req: VehiculoCreate,
    current_persona: Persona = Depends(get_current_persona),
    db: AsyncSession = Depends(get_db)
):
    # Verificar que la matrícula no exista
    existing = await db.execute(select(Vehiculo).where(Vehiculo.matricula == req.matricula))
    if existing.scalar_one_or_none():
        raise HTTPException(400, "Matrícula ya registrada")
    
    vehiculo_data = req.dict()
    vehiculo_data["id_persona"] = current_persona.id
    nuevo = await crud_vehiculo.create(db, vehiculo_data)
    return nuevo

@router.put("/{vehiculo_id}", response_model=VehiculoResponse)
async def update_vehiculo(
    vehiculo_id: int,
    req: VehiculoUpdate,
    current_persona: Persona = Depends(get_current_persona),
    db: AsyncSession = Depends(get_db)
):
    vehiculo = await crud_vehiculo.get(db, vehiculo_id)
    if not vehiculo or vehiculo.id_persona != current_persona.id:
        raise HTTPException(404, "Vehículo no encontrado")
    
    # Si se actualiza matrícula, verificar unicidad
    if req.matricula and req.matricula != vehiculo.matricula:
        existing = await db.execute(select(Vehiculo).where(Vehiculo.matricula == req.matricula))
        if existing.scalar_one_or_none():
            raise HTTPException(400, "Matrícula ya registrada")
    
    update_data = req.dict(exclude_unset=True)
    vehiculo = await crud_vehiculo.update(db, vehiculo, update_data)
    return vehiculo

@router.delete("/{vehiculo_id}", status_code=204)
async def delete_vehiculo(
    vehiculo_id: int,
    current_persona: Persona = Depends(get_current_persona),
    db: AsyncSession = Depends(get_db)
):
    vehiculo = await crud_vehiculo.get(db, vehiculo_id)
    if not vehiculo or vehiculo.id_persona != current_persona.id:
        raise HTTPException(404, "Vehículo no encontrado")
    await crud_vehiculo.delete(db, vehiculo_id)
    return Response(status_code=204)