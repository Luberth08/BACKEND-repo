import asyncio
import sys
from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.models.persona import Persona
from app.models.usuario import Usuario
from app.models.rol import Rol
from app.models.rol_usuario import RolUsuario
from app.core.constants import ROL_ADMIN_SISTEMA

async def set_admin(email: str):
    async with AsyncSessionLocal() as db:
        # Buscar persona
        res = await db.execute(select(Persona).where(Persona.email == email))
        persona = res.scalar_one_or_none()
        if not persona:
            print(f"No se encontró ninguna persona con el correo {email}")
            return
            
        # Buscar usuario
        res = await db.execute(select(Usuario).where(Usuario.id_persona == persona.id))
        usuario = res.scalar_one_or_none()
        if not usuario:
            print(f"La persona {email} no ha completado su registro de usuario.")
            return

        # Buscar rol admin
        res = await db.execute(select(Rol).where(Rol.nombre == ROL_ADMIN_SISTEMA))
        rol_admin = res.scalar_one_or_none()
        if not rol_admin:
            print(f"Error: El rol '{ROL_ADMIN_SISTEMA}' no existe en la base de datos.")
            return

        # Verificar si ya tiene el rol
        res = await db.execute(
            select(RolUsuario)
            .where(RolUsuario.id_usuario == usuario.id)
            .where(RolUsuario.id_rol == rol_admin.id)
        )
        if res.scalar_one_or_none():
            print(f"El usuario {email} YA es Administrador del Sistema.")
            return

        # Asignar rol
        nuevo_rol = RolUsuario(id_usuario=usuario.id, id_rol=rol_admin.id)
        db.add(nuevo_rol)
        await db.commit()
        print(f"¡Éxito! Se le ha dado el rol de Administrador del Sistema a {email}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python dar_admin.py <correo_del_usuario>")
    else:
        asyncio.run(set_admin(sys.argv[1]))
