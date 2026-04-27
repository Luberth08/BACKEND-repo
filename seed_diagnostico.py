import asyncio
import sys
from sqlalchemy import select, text
from app.db.session import AsyncSessionLocal
from app.models.persona import Persona
from app.models.solicitud_diagnostico import SolicitudDiagnostico, EstadoSolicitudDiagnostico
from app.models.diagnostico import Diagnostico

async def seed_diagnostico(email: str):
    async with AsyncSessionLocal() as db:
        # 1. Buscar la persona por email
        res = await db.execute(select(Persona).where(Persona.email == email))
        persona = res.scalar_one_or_none()
        
        if not persona:
            print(f"Error: No se encontró un usuario con el correo {email}")
            return
            
        # 2. Insertar solicitud_diagnostico usando raw SQL para manejar PostGIS Geography fácilmente
        res = await db.execute(
            text("""
                INSERT INTO solicitud_diagnostico (descripcion, estado, ubicacion, id_persona)
                VALUES ('Mi auto hace un ruido raro y se apagó', 'diagnosticada', ST_SetSRID(ST_MakePoint(-63.1821, -17.7833), 4326), :persona_id)
                RETURNING id;
            """),
            {"persona_id": persona.id}
        )
        sol_diag_id = res.scalar()
        
        # 3. Insertar diagnostico
        nuevo_diag = Diagnostico(
            descripcion="Falla en la bomba de combustible o sistema eléctrico (Generado para Test E2E)",
            nivel_confianza=0.85,
            id_solicitud_diagnostico=sol_diag_id
        )
        db.add(nuevo_diag)
        await db.commit()
        await db.refresh(nuevo_diag)
        
        print(f"¡Éxito! Se ha creado el diagnostico_id: {nuevo_diag.id} para el usuario {email}")
        print(f"Ahora puedes usar el ID {nuevo_diag.id} en la URL de tu petición en Thunder Client.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python seed_diagnostico.py <correo_del_cliente>")
    else:
        asyncio.run(seed_diagnostico(sys.argv[1]))
