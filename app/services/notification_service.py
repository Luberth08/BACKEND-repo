"""
Servicio para envío de notificaciones push usando Firebase Cloud Messaging (FCM)
"""
import logging
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import httpx
import json

from app.models.dispositivo_usuario import DispositivoUsuario
from app.models.persona import Persona
from app.models.servicio import Servicio
from app.models.solicitud_servicio import SolicitudServicio
from app.models.solicitud_diagnostico import SolicitudDiagnostico
from app.models.diagnostico import Diagnostico
from app.crud import crud_dispositivo_usuario
from app.core.config import settings

logger = logging.getLogger(__name__)

class NotificationService:
    """Servicio para gestionar notificaciones push"""
    
    def __init__(self):
        # Configuración FCM (agregar a settings)
        self.fcm_server_key = getattr(settings, 'FCM_SERVER_KEY', None)
        self.fcm_url = "https://fcm.googleapis.com/fcm/send"
    
    async def enviar_notificacion_push(
        self,
        tokens: List[str],
        titulo: str,
        mensaje: str,
        datos_extra: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Envía notificación push a una lista de tokens FCM
        """
        if not self.fcm_server_key:
            logger.warning("FCM_SERVER_KEY no configurado, no se pueden enviar notificaciones")
            return False
        
        if not tokens:
            logger.info("No hay tokens FCM para enviar notificación")
            return True
        
        # Preparar payload FCM
        payload = {
            "registration_ids": tokens,
            "notification": {
                "title": titulo,
                "body": mensaje,
                "sound": "default",
                "badge": 1
            },
            "data": datos_extra or {}
        }
        
        headers = {
            "Authorization": f"key={self.fcm_server_key}",
            "Content-Type": "application/json"
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    self.fcm_url,
                    json=payload,
                    headers=headers
                )
                
                if response.status_code == 200:
                    result = response.json()
                    success_count = result.get('success', 0)
                    failure_count = result.get('failure', 0)
                    
                    logger.info(f"Notificación enviada: {success_count} éxitos, {failure_count} fallos")
                    
                    # TODO: Manejar tokens inválidos (eliminar de BD)
                    if failure_count > 0:
                        logger.warning(f"Algunos tokens FCM fallaron: {result.get('results', [])}")
                    
                    return success_count > 0
                else:
                    logger.error(f"Error FCM: {response.status_code} - {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error enviando notificación FCM: {e}")
            return False
    
    async def obtener_tokens_persona(self, db: AsyncSession, id_persona: int) -> List[str]:
        """
        Obtiene todos los tokens FCM de una persona
        """
        dispositivos = await crud_dispositivo_usuario.dispositivo_usuario.get_by_persona(db, id_persona)
        return [d.token_fcm for d in dispositivos if d.token_fcm]
    
    async def notificar_solicitud_aceptada(
        self,
        db: AsyncSession,
        servicio: Servicio
    ) -> bool:
        """
        Notifica al cliente que su solicitud fue aceptada
        """
        try:
            # Obtener datos del cliente
            result = await db.execute(
                select(SolicitudDiagnostico, Persona).join(
                    Diagnostico, SolicitudDiagnostico.id == Diagnostico.id_solicitud_diagnostico
                ).join(
                    SolicitudServicio, Diagnostico.id == SolicitudServicio.id_diagnostico
                ).join(
                    Persona, SolicitudDiagnostico.id_persona == Persona.id
                ).where(
                    SolicitudServicio.id == servicio.id_solicitud_servicio
                )
            )
            
            row = result.first()
            if not row:
                logger.warning(f"No se encontró cliente para servicio {servicio.id}")
                return False
            
            solicitud_diag, persona = row
            
            # Obtener tokens FCM del cliente
            tokens = await self.obtener_tokens_persona(db, persona.id)
            
            if not tokens:
                logger.info(f"Cliente {persona.id} no tiene tokens FCM registrados")
                return True
            
            # Enviar notificación
            titulo = "¡Solicitud Aceptada!"
            mensaje = f"Un taller ha aceptado tu solicitud de servicio. El técnico está en camino."
            
            datos_extra = {
                "tipo": "solicitud_aceptada",
                "servicio_id": str(servicio.id),
                "accion": "abrir_servicio_detalle"
            }
            
            return await self.enviar_notificacion_push(tokens, titulo, mensaje, datos_extra)
            
        except Exception as e:
            logger.error(f"Error notificando solicitud aceptada: {e}")
            return False
    
    async def notificar_cambio_estado_servicio(
        self,
        db: AsyncSession,
        servicio: Servicio,
        estado_anterior: str,
        estado_nuevo: str
    ) -> bool:
        """
        Notifica al cliente sobre cambios de estado del servicio
        """
        try:
            # Obtener datos del cliente
            result = await db.execute(
                select(SolicitudDiagnostico, Persona).join(
                    Diagnostico, SolicitudDiagnostico.id == Diagnostico.id_solicitud_diagnostico
                ).join(
                    SolicitudServicio, Diagnostico.id == SolicitudServicio.id_diagnostico
                ).join(
                    Persona, SolicitudDiagnostico.id_persona == Persona.id
                ).where(
                    SolicitudServicio.id == servicio.id_solicitud_servicio
                )
            )
            
            row = result.first()
            if not row:
                return False
            
            solicitud_diag, persona = row
            
            # Obtener tokens FCM del cliente
            tokens = await self.obtener_tokens_persona(db, persona.id)
            
            if not tokens:
                return True
            
            # Generar mensaje según el estado
            titulo, mensaje = self._generar_mensaje_estado(estado_nuevo)
            
            datos_extra = {
                "tipo": "cambio_estado_servicio",
                "servicio_id": str(servicio.id),
                "estado_anterior": estado_anterior,
                "estado_nuevo": estado_nuevo,
                "accion": "abrir_servicio_detalle"
            }
            
            return await self.enviar_notificacion_push(tokens, titulo, mensaje, datos_extra)
            
        except Exception as e:
            logger.error(f"Error notificando cambio de estado: {e}")
            return False
    
    async def notificar_servicio_finalizado(
        self,
        db: AsyncSession,
        servicio: Servicio
    ) -> bool:
        """
        Notifica al cliente que su servicio ha sido finalizado
        """
        try:
            # Obtener datos del cliente
            result = await db.execute(
                select(SolicitudDiagnostico, Persona).join(
                    Diagnostico, SolicitudDiagnostico.id == Diagnostico.id_solicitud_diagnostico
                ).join(
                    SolicitudServicio, Diagnostico.id == SolicitudServicio.id_diagnostico
                ).join(
                    Persona, SolicitudDiagnostico.id_persona == Persona.id
                ).where(
                    SolicitudServicio.id == servicio.id_solicitud_servicio
                )
            )
            
            row = result.first()
            if not row:
                return False
            
            solicitud_diag, persona = row
            
            # Obtener tokens FCM del cliente
            tokens = await self.obtener_tokens_persona(db, persona.id)
            
            if not tokens:
                return True
            
            # Enviar notificación
            titulo = "¡Servicio Completado!"
            mensaje = "Tu servicio ha sido finalizado exitosamente. ¡No olvides valorar tu experiencia!"
            
            datos_extra = {
                "tipo": "servicio_finalizado",
                "servicio_id": str(servicio.id),
                "accion": "abrir_valoracion"
            }
            
            return await self.enviar_notificacion_push(tokens, titulo, mensaje, datos_extra)
            
        except Exception as e:
            logger.error(f"Error notificando servicio finalizado: {e}")
            return False
    
    def _generar_mensaje_estado(self, estado: str) -> tuple[str, str]:
        """
        Genera título y mensaje según el estado del servicio
        """
        mensajes = {
            "tecnico_asignado": (
                "Técnico Asignado",
                "Se ha asignado un técnico a tu servicio"
            ),
            "en_camino": (
                "Técnico en Camino",
                "El técnico está en camino hacia tu ubicación"
            ),
            "en_lugar": (
                "Técnico en el Lugar",
                "El técnico ha llegado a tu ubicación"
            ),
            "en_atencion": (
                "Servicio en Atención",
                "El técnico está trabajando en tu vehículo"
            ),
            "finalizado": (
                "¡Servicio Completado!",
                "Tu servicio ha sido finalizado exitosamente"
            ),
            "cancelado": (
                "Servicio Cancelado",
                "Tu servicio ha sido cancelado"
            )
        }
        
        return mensajes.get(estado, ("Actualización de Servicio", f"Tu servicio cambió a: {estado}"))

# Instancia global del servicio
notification_service = NotificationService()