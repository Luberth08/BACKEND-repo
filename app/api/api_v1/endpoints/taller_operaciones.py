from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.api.api_v1 import deps
from app.models.usuario import Usuario
from app.models.taller import Taller
from app.models.solicitud_afiliacion import SolicitudAfiliacion
from app.models.empleado import Empleado, EstadoEmpleado
from app.models.vehiculo_taller import VehiculoTaller, EstadoVehiculoTaller
from app.models.solicitud_servicio import SolicitudServicio, EstadoSolicitudServicio
from app.models.servicio import Servicio, EstadoServicio
from app.models.servicio_tecnico import ServicioTecnico
from app.models.servicio_vehiculo import ServicioVehiculo
from app.models.historial_estados_servicio import HistorialEstadosServicio
from app.schemas.operaciones import SolicitudServicioResponse, AsignacionServicioCreate, ServicioResponse

router = APIRouter()

async def get_taller_del_usuario(db: AsyncSession, user: Usuario):
    result_af = await db.execute(select(SolicitudAfiliacion).filter(SolicitudAfiliacion.id_usuario_solicita == user.id))
    afiliacion = result_af.scalars().first()
    if not afiliacion:
        raise HTTPException(status_code=403, detail="Usuario no posee una solicitud de afiliacion vinculada.")
    
    result_taller = await db.execute(select(Taller).filter(Taller.id_solicitud_afiliacion == afiliacion.id))
    taller = result_taller.scalars().first()
    if not taller:
        raise HTTPException(status_code=403, detail="Taller no registrado o no aprobado.")
    return taller

@router.get("/solicitudes", response_model=List[SolicitudServicioResponse])
async def listar_solicitudes_taller(
    db: AsyncSession = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_usuario)
):
    """ Taller verifica qué solicitudes entrantes tiene sugeridas por la IA """
    taller = await get_taller_del_usuario(db, current_user)
    
    result = await db.execute(select(SolicitudServicio).filter(
        SolicitudServicio.id_taller == taller.id,
        SolicitudServicio.estado == EstadoSolicitudServicio.ofertada
    ))
    solicitudes = result.scalars().all()
    
    return solicitudes

@router.post("/solicitudes/{id_solicitud}/aceptar", response_model=ServicioResponse)
async def aceptar_solicitud_y_asignar(
    id_solicitud: int,
    asignacion: AsignacionServicioCreate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_usuario)
):
    taller = await get_taller_del_usuario(db, current_user)
    
    result_sol = await db.execute(select(SolicitudServicio).filter(
        SolicitudServicio.id == id_solicitud,
        SolicitudServicio.id_taller == taller.id,
        SolicitudServicio.estado == EstadoSolicitudServicio.ofertada
    ))
    solicitud = result_sol.scalars().first()
    
    if not solicitud:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada o ya procesada.")
        
    solicitud.estado = EstadoSolicitudServicio.aceptada
    solicitud.costo_estimado = asignacion.costo_final
    
    nuevo_servicio = Servicio(
        estado=EstadoServicio.asignado,
        id_solicitud_servicio=solicitud.id
    )
    db.add(nuevo_servicio)
    await db.flush()
    
    for id_emp in asignacion.id_empleados:
        res_emp = await db.execute(select(Empleado).filter(Empleado.id == id_emp, Empleado.id_taller == taller.id))
        empleado = res_emp.scalars().first()
        if not empleado:
            raise HTTPException(status_code=400, detail=f"Empleado {id_emp} no pertenece al taller.")
        empleado.estado = EstadoEmpleado.ocupado
        st = ServicioTecnico(id_servicio=nuevo_servicio.id, id_empleado=id_emp)
        db.add(st)
        
    for id_veh in asignacion.id_vehiculos_taller:
        res_veh = await db.execute(select(VehiculoTaller).filter(VehiculoTaller.id == id_veh, VehiculoTaller.id_taller == taller.id))
        vehiculo = res_veh.scalars().first()
        if not vehiculo:
            raise HTTPException(status_code=400, detail=f"Vehiculo {id_veh} no listado en inventario.")
        vehiculo.estado = EstadoVehiculoTaller.en_servicio
        sv = ServicioVehiculo(id_servicio=nuevo_servicio.id, id_vehiculo_taller=id_veh)
        db.add(sv)
        
    historial = HistorialEstadosServicio(
        estado=EstadoServicio.asignado,
        id_servicio=nuevo_servicio.id
    )
    db.add(historial)
    
    await db.commit()
    await db.refresh(nuevo_servicio)
    return nuevo_servicio
