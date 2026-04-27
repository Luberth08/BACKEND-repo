import asyncio
from sqlalchemy import text
from app.db.session import AsyncSessionLocal

async def seed():
    async with AsyncSessionLocal() as db:
        # Insertar 2 especialidades básicas si no existen
        await db.execute(text("""
            INSERT INTO especialidad (id, nombre, descripcion) 
            VALUES 
            (1, 'Mecánica General', 'Reparaciones generales de motor y piezas'),
            (2, 'Grúa', 'Servicio de remolque')
            ON CONFLICT (id) DO NOTHING;
        """))
        await db.commit()
        print("Especialidades básicas (IDs 1 y 2) insertadas correctamente.")

if __name__ == "__main__":
    asyncio.run(seed())
