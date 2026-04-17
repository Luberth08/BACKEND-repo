from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import Optional
from app.models.taller import Taller, EstadoTaller
from app.models.vehiculo_taller import VehiculoTaller, EstadoVehiculoTaller
from app.models.empleado import Empleado, EstadoEmpleado

async def buscar_taller_adecuado(
    db: AsyncSession, 
    lat: float, 
    lon: float, 
    requiere_remolque: bool, 
    radio_km: float = 15.0
) -> Optional[Taller]:
    """
    Algoritmo de asignación que recomienda el Taller ideal 
    basado en la ubicación (PostGIS), disponibilidad de técnicos 
    y si necesita grúa, de forma completamente asíncrona.
    """
    user_location = f'POINT({lon} {lat})'
    
    query = select(Taller).filter(
        Taller.estado == EstadoTaller.activo,
        func.ST_DWithin(Taller.ubicacion, func.ST_GeographyFromText(user_location), radio_km * 1000)
    )
    
    if requiere_remolque:
        # Subquery para grúas
        subq_vehiculo = select(VehiculoTaller).filter(
            VehiculoTaller.id_taller == Taller.id,
            VehiculoTaller.tipo == "camion",
            VehiculoTaller.estado == EstadoVehiculoTaller.disponible
        )
        query = query.filter(subq_vehiculo.exists())
    
    # Subquery para empleados
    subq_empleado = select(Empleado).filter(
        Empleado.id_taller == Taller.id,
        Empleado.estado == EstadoEmpleado.activo
    )
    query = query.filter(subq_empleado.exists())

    # Criterio principal: Ordenado por el más cercano geográficamente
    query = query.order_by(
        func.ST_Distance(Taller.ubicacion, func.ST_GeographyFromText(user_location)).asc()
    )
    
    result = await db.execute(query)
    return result.scalars().first()
