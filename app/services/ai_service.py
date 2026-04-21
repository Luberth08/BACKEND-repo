import os
import logging
from decimal import Decimal
from typing import List, Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


async def transcribe_audio_mock(file_path: str) -> str:
    """Mock transcription: returns a placeholder text including filename."""
    try:
        name = os.path.basename(file_path)
        return f"[TRANSCRIPCIÓN MOCK] archivo: {name}"
    except Exception as e:
        logger.exception("Error en transcripción mock")
        return ""


async def generar_diagnostico_mock(descripcion_texto: str, imagen_urls: List[str], transcripcion: Optional[str], vehiculo_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Genera un diagnóstico simulado basado en palabras clave.

    Retorna un dict con: descripcion, nivel_confianza, fecha, incidentes: list of {concepto, nivel_confianza, sugerido_por}
    """
    texto = (descripcion_texto or "") + " " + (transcripcion or "")
    texto_lower = texto.lower()
    posibles = []

    keywords = {
        "llanta": ["llanta", "ponch", "pinch"],
        "freno": ["freno", "frenos"],
        "motor": ["motor", "no enciende", "calienta", "enciende"],
        "bateria": ["bateria", "batería", "batt"],
        "colision": ["choque", "colision", "accident", "colisión"],
    }

    for concepto, keys in keywords.items():
        score = 0.0
        for k in keys:
            if k in texto_lower:
                score += 0.8
        if score > 0:
            # normalize score
            nivel = min(1.0, 0.6 + score * 0.1)
            posibles.append({
                "concepto": concepto,
                "nivel_confianza": round(nivel, 4),
                "sugerido_por": "ia"
            })

    # fallback: si no detectó nada, sugerir "desconocido" con baja confianza
    if not posibles:
        posibles.append({
            "concepto": "desconocido",
            "nivel_confianza": 0.5,
            "sugerido_por": "ia"
        })

    # nivel general = average
    niveles = [Decimal(str(p["nivel_confianza"])) for p in posibles]
    nivel_general = (sum(niveles) / Decimal(len(niveles))) if niveles else Decimal("0.0")

    descripcion = "Diagnóstico generado por IA (mock)."
    if vehiculo_info:
        descripcion += f" Vehículo: {vehiculo_info.get('matricula', '')}."

    return {
        "descripcion": descripcion,
        "nivel_confianza": float(round(nivel_general, 4)),
        "fecha": datetime.utcnow(),
        "incidentes": posibles
    }


# Adapter functions: use these from other modules. Currently delegate to mocks.
USE_REAL_AI = os.environ.get("USE_REAL_AI", "false").lower() in ("1", "true", "yes")


async def transcribe_audio(file_path: str) -> str:
    """Adapter for audio transcription. If `USE_REAL_AI` is enabled, this
    function should call the real provider. For now it delegates to the mock.
    """
    if USE_REAL_AI:
        logger.debug("USE_REAL_AI enabled but no provider implemented; falling back to mock")
        # future: call real provider here
    return await transcribe_audio_mock(file_path)


async def generar_diagnostico(descripcion_texto: str, imagen_urls: List[str], transcripcion: Optional[str], vehiculo_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Adapter for generating a multimodal diagnóstico. Delegates to mock.

    Expected return dict keys: descripcion (str), nivel_confianza (float), fecha (datetime), incidentes (list[dict])
    """
    if USE_REAL_AI:
        logger.debug("USE_REAL_AI enabled but no provider implemented; falling back to mock")
        # future: call real provider here
    return await generar_diagnostico_mock(descripcion_texto, imagen_urls, transcripcion, vehiculo_info)
