"""
Script para poblar la tabla tipo_incidente con datos iniciales
Ejecutar: python seed_tipos_incidente.py
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.tipo_incidente import TipoIncidente

# Tipos de incidentes comunes
TIPOS_INCIDENTES = [
    {"concepto": "falla_motor", "prioridad": 1, "requiere_remolque": True},
    {"concepto": "problema_frenos", "prioridad": 1, "requiere_remolque": True},
    {"concepto": "fuga_aceite", "prioridad": 2, "requiere_remolque": False},
    {"concepto": "bateria_descargada", "prioridad": 2, "requiere_remolque": False},
    {"concepto": "neumatico_pinchado", "prioridad": 2, "requiere_remolque": False},
    {"concepto": "sobrecalentamiento", "prioridad": 1, "requiere_remolque": True},
    {"concepto": "problema_transmision", "prioridad": 1, "requiere_remolque": True},
    {"concepto": "falla_electrica", "prioridad": 2, "requiere_remolque": False},
    {"concepto": "problema_suspension", "prioridad": 2, "requiere_remolque": False},
    {"concepto": "fuga_combustible", "prioridad": 1, "requiere_remolque": True},
    {"concepto": "problema_direccion", "prioridad": 1, "requiere_remolque": True},
    {"concepto": "ruido_anormal", "prioridad": 3, "requiere_remolque": False},
    {"concepto": "vibracion_excesiva", "prioridad": 3, "requiere_remolque": False},
    {"concepto": "luz_check_engine", "prioridad": 2, "requiere_remolque": False},
    {"concepto": "problema_arranque", "prioridad": 2, "requiere_remolque": False},
    {"concepto": "falla_aire_acondicionado", "prioridad": 3, "requiere_remolque": False},
    {"concepto": "problema_escape", "prioridad": 3, "requiere_remolque": False},
    {"concepto": "falla_embrague", "prioridad": 2, "requiere_remolque": False},
    {"concepto": "informacion_insuficiente", "prioridad": 3, "requiere_remolque": False},
    {"concepto": "desconocido", "prioridad": 3, "requiere_remolque": False},
]

async def seed_tipos_incidente():
    """Pobla la tabla tipo_incidente con datos iniciales"""
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        try:
            # Verificar si ya hay datos
            from sqlalchemy import select, func
            result = await session.execute(select(func.count(TipoIncidente.id)))
            count = result.scalar()
            
            if count > 0:
                print(f"✅ La tabla tipo_incidente ya tiene {count} registros")
                return
            
            print("📝 Insertando tipos de incidentes...")
            
            for tipo_data in TIPOS_INCIDENTES:
                tipo = TipoIncidente(**tipo_data)
                session.add(tipo)
            
            await session.commit()
            print(f"✅ Se insertaron {len(TIPOS_INCIDENTES)} tipos de incidentes")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            await session.rollback()
        finally:
            await engine.dispose()

if __name__ == "__main__":
    asyncio.run(seed_tipos_incidente())
