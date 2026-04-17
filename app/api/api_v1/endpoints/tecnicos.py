from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.api.api_v1 import deps
from app.models.usuario import Usuario
from app.models.empleado import Empleado, EstadoEmpleado
from app.models.servicio import Servicio, EstadoServicio
from app.models.historial_estados_servicio import HistorialEstadosServicio
from app.models.servicio_tecnico import ServicioTecnico
from app.schemas.operaciones import ActualizarEstadoServicio, ServicioResponse
from app.api.websockets.notificaciones import notificar_usuario

router = APIRouter()

@router.put("/{id_servicio}/estado", response_model=ServicioResponse)
async def actualizar_estado_servicio(
    id_servicio: int,
    actualizacion: ActualizarEstadoServicio,
    db: AsyncSession = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_usuario)
):
    res_emp = await db.execute(select(Empleado).filter(Empleado.id_usuario == current_user.id))
    empleado = res_emp.scalars().first()
    if not empleado:
        raise HTTPException(status_code=403, detail="El usuario actual no es un empleado registrado.")
        
    res_st = await db.execute(select(ServicioTecnico).filter(
        ServicioTecnico.id_servicio == id_servicio,
        ServicioTecnico.id_empleado == empleado.id
    ))
    st = res_st.scalars().first()
    if not st:
        raise HTTPException(status_code=403, detail="No estas asignado a este servicio.")
        
    res_serv = await db.execute(select(Servicio).filter(Servicio.id == id_servicio))
    servicio = res_serv.scalars().first()
    if not servicio:
        raise HTTPException(status_code=404, detail="Servicio no encontrado.")
        
    servicio.estado = actualizacion.nuevo_estado
    
    if actualizacion.nuevo_estado in [EstadoServicio.finalizado, EstadoServicio.cancelado]:
        empleado.estado = EstadoEmpleado.activo
    
    historial = HistorialEstadosServicio(
        estado=actualizacion.nuevo_estado,
        id_servicio=servicio.id
    )
    db.add(historial)
    
    await db.commit()
    await db.refresh(servicio)
    
    # Notificar asíncronamente al sistema logistico/cliente 
    # El id del cliente originario estaria en SolicitudDiagnostico.id_vehiculo.persona.usuario
    # Se notifica al general
    await notificar_usuario(f"Servicio_{id_servicio}_update", f"El estado del rescate cruzó a {actualizacion.nuevo_estado}")
    
    return servicio
