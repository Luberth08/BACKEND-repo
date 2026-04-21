import os
import uuid
import logging
from decimal import Decimal
from typing import List, Optional, Dict, Any
from shapely.geometry import Point
from geoalchemy2.shape import from_shape
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import UploadFile
from sqlalchemy import select

from app.crud import (
    solicitud_diagnostico,
    evidencia as evidencia_crud,
    diagnostico as diagnostico_crud,
    tipo_incidente as tipo_incidente_crud,
    incidente as incidente_crud,
    vehiculo as crud_vehiculo
)
from app.services.ai_service import transcribe_audio, generar_diagnostico
from app.models.solicitud_diagnostico import EstadoSolicitudDiagnostico

logger = logging.getLogger(__name__)

UPLOAD_DIR = os.path.join("static", "uploads", "diagnosticos")


def _ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


async def _save_upload_file(file: UploadFile, dest_folder: str) -> str:
    _ensure_dir(dest_folder)
    ext = os.path.splitext(file.filename)[1] or ""
    filename = f"{uuid.uuid4().hex}{ext}"
    dest_path = os.path.join(dest_folder, filename)
    # leer contenido
    content = await file.read()
    with open(dest_path, "wb") as f:
        f.write(content)
    # devolver url pública (montada en /static)
    return f"/static/uploads/diagnosticos/{filename}"


async def crear_solicitud_diagnostico(
    db: AsyncSession,
    id_persona: int,
    descripcion: str,
    ubicacion_str: str,
    matricula: Optional[str] = None,
    vehiculo_data: Optional[Dict[str, Any]] = None,
    fotos: Optional[List[UploadFile]] = None,
    audio: Optional[UploadFile] = None
):
    """Crea solicitud, guarda evidencias, llama IA mock y crea diagnóstico/incidentes.

    - Guarda archivos en `static/uploads/diagnosticos`
    - Transcribe audio (mock)
    - Genera diagnóstico (mock)
    - Si IA falla, deja estado 'error' y permite reintento
    """
    # parsear ubicación (esperamos 'lat,lon')
    try:
        lat, lon = map(float, ubicacion_str.split(","))
        point = Point(lon, lat)
        ubicacion_geog = from_shape(point, srid=4326)
    except Exception:
        raise ValueError("Ubicación inválida. Use formato 'lat,lon'")

    # Vehículo: buscar por matrícula exacta
    veh = None
    if matricula:
        veh = await crud_vehiculo.get_by_matricula(db, matricula)

    # Si no existe vehículo y se dieron datos, crearlo
    if not veh and vehiculo_data and vehiculo_data.get("matricula"):
        data = vehiculo_data.copy()
        data["id_persona"] = id_persona
        veh = await crud_vehiculo.create(db, data)

    # Crear solicitud (sin diagnostico aún)
    solicitud_data = {
        "descripcion": descripcion,
        "ubicacion": ubicacion_geog,
        "id_persona": id_persona,
        "id_vehiculo": veh.id if veh else None,
    }
    solicitud = await solicitud_diagnostico.create(db, solicitud_data)

    # Preparar carpeta de uploads para esta solicitud
    folder = os.path.join(UPLOAD_DIR)
    _ensure_dir(folder)

    imagen_urls = []
    transcripcion_text = None

    # Guardar fotos (max 3)
    if fotos:
        fotos = fotos[:3]
        for f in fotos:
            url = await _save_upload_file(f, folder)
            imagen_urls.append(url)
            await evidencia_crud.create(db, {"url": url, "tipo": "imagen", "id_solicitud_diagnostico": solicitud.id})

    # Guardar audio y transcribir
    if audio:
        audio_url = await _save_upload_file(audio, folder)
        # transcribir (mock)
        audio_path = os.path.join(folder, os.path.basename(audio_url))
        try:
                transcripcion_text = await transcribe_audio(audio_path)
        except Exception:
            transcripcion_text = None
        await evidencia_crud.create(db, {"url": audio_url, "tipo": "audio", "transcripcion": transcripcion_text, "id_solicitud_diagnostico": solicitud.id})

    # Commit inicial para persistir solicitud y evidencias
    await db.commit()

    # Llamada a IA (mock). Si falla, actualizar estado a 'error' y permitir reintento.
    try:
        result = await generar_diagnostico(descripcion, imagen_urls, transcripcion_text, {"matricula": veh.matricula} if veh else None)
        # crear diagnostico e incidentes
        nivel_general = Decimal(str(result.get("nivel_confianza", 0)))
        diag = await diagnostico_crud.create(db, {
            "descripcion": result.get("descripcion"),
            "nivel_confianza": nivel_general,
            "id_solicitud_diagnostico": solicitud.id
        })

        for inc in result.get("incidentes", []):
            # asegurar tipo_incidente existe
            tipo = await tipo_incidente_crud.get_by_concepto(db, inc["concepto"]) if isinstance(inc, dict) else None
            if not tipo:
                # crear tipo_incidente básico
                tipo = await tipo_incidente_crud.create(db, {"concepto": inc["concepto"], "prioridad": 3, "requiere_remolque": False})
            nivel = Decimal(str(inc.get("nivel_confianza", 0)))
            await incidente_crud.create(db, {"id_diagnostico": diag.id, "id_tipo_incidente": tipo.id, "sugerido_por": inc.get("sugerido_por", "ia"), "nivel_confianza": nivel})

        # actualizar estado solicitud
        await solicitud_diagnostico.update_estado(db, solicitud.id, EstadoSolicitudDiagnostico.diagnosticada)
        await db.commit()
    except Exception as e:
        logger.exception("Error procesando IA para solicitud %s", solicitud.id)
        # marcar error
        await solicitud_diagnostico.update_estado(db, solicitud.id, EstadoSolicitudDiagnostico.error)
        await db.commit()

    # Recargar solicitud con relaciones
    solicitud_final = await solicitud_diagnostico.get(db, solicitud.id)
    return solicitud_final


async def reintentar_procesamiento(db: AsyncSession, solicitud_id: int):
    solicitud = await solicitud_diagnostico.get(db, solicitud_id)
    if not solicitud:
        return None
    if solicitud.estado == EstadoSolicitudDiagnostico.diagnosticada:
        return solicitud

    # recolectar evidencias
    from app.crud.crud_evidencia import evidencia as evidencia_crud_local
    evids = await db.execute(select(evidencia_crud_local.model).where(evidencia_crud_local.model.id_solicitud_diagnostico == solicitud_id))
    evids = evids.scalars().all()
    imagen_urls = [e.url for e in evids if getattr(e, 'tipo').value == 'imagen' or getattr(e, 'tipo') == 'imagen']
    transcripcion = None
    for e in evids:
        if getattr(e, 'tipo').value == 'audio' or getattr(e, 'tipo') == 'audio':
            transcripcion = e.transcripcion

    # volver a llamar IA
    try:
        result = await generar_diagnostico(solicitud.descripcion or "", imagen_urls, transcripcion, None)
        nivel_general = Decimal(str(result.get("nivel_confianza", 0)))
        diag = await diagnostico_crud.create(db, {
            "descripcion": result.get("descripcion"),
            "nivel_confianza": nivel_general,
            "id_solicitud_diagnostico": solicitud.id
        })
        for inc in result.get("incidentes", []):
            tipo = await tipo_incidente_crud.get_by_concepto(db, inc["concepto"]) if isinstance(inc, dict) else None
            if not tipo:
                tipo = await tipo_incidente_crud.create(db, {"concepto": inc["concepto"], "prioridad": 3, "requiere_remolque": False})
            nivel = Decimal(str(inc.get("nivel_confianza", 0)))
            await incidente_crud.create(db, {"id_diagnostico": diag.id, "id_tipo_incidente": tipo.id, "sugerido_por": inc.get("sugerido_por", "ia"), "nivel_confianza": nivel})
        await solicitud_diagnostico.update_estado(db, solicitud.id, EstadoSolicitudDiagnostico.diagnosticada)
        await db.commit()
    except Exception:
        await solicitud_diagnostico.update_estado(db, solicitud.id, EstadoSolicitudDiagnostico.error)
        await db.commit()

    return await solicitud_diagnostico.get(db, solicitud.id)
