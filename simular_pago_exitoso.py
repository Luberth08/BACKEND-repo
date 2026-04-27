import asyncio
import sys
from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.models.servicio import Servicio, EstadoServicio
from app.models.factura import Factura, EstadoPago
from datetime import datetime, timezone

async def simular_pago(servicio_id: int):
    async with AsyncSessionLocal() as db:
        # 1. Buscar el servicio
        servicio = await db.get(Servicio, servicio_id)
        if not servicio:
            print(f"Error: No se encontró el servicio con ID {servicio_id}")
            return

        # 2. Buscar o crear la factura
        res = await db.execute(select(Factura).where(Factura.id_servicio == servicio_id))
        factura = res.scalar_one_or_none()
        
        if not factura:
            # Crear una factura dummy si no existe
            factura = Factura(
                id_servicio=servicio_id,
                monto_total=250.0,
                comision_plataforma=25.0,
                estado_pago=EstadoPago.pendiente
            )
            db.add(factura)
            await db.flush()

        # 3. Marcar como pagada y finalizar servicio
        factura.estado_pago = EstadoPago.pagado
        factura.fecha_pago = datetime.now(timezone.utc)
        factura.metodo_pago = "stripe_simulado"
        
        servicio.estado = EstadoServicio.finalizado
        
        await db.commit()
        print(f"¡Éxito! El servicio {servicio_id} ha sido FINALIZADO y la factura marcada como PAGADA.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python simular_pago_exitoso.py <servicio_id>")
    else:
        asyncio.run(simular_pago(int(sys.argv[1])))
