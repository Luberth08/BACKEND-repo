"""
Servicio de IA para diagnóstico vehicular
Usa Groq API para LLM, CLIP para imágenes, Whisper para audio
"""
import os
import logging
import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.core.config import settings

logger = logging.getLogger(__name__)

# ============================================================
# CONFIGURACIÓN
# ============================================================
WHISPER_MODEL_SIZE = settings.WHISPER_MODEL_SIZE
GROQ_API_KEY = settings.GROQ_API_KEY or ""
GROQ_MODEL = settings.GROQ_MODEL
USE_REAL_AI = settings.USE_REAL_AI

# Caché de modelos (singleton)
_CLIP_MODEL = None
_CLIP_PREPROCESS = None
_WHISPER_MODEL = None

# ============================================================
# IMPORTS DE LIBRERÍAS
# ============================================================
try:
    import torch
    import clip
    from faster_whisper import WhisperModel
    from groq import Groq
    from PIL import Image
except ImportError as e:
    logger.critical(f"Faltan dependencias de IA: {e}")
    raise RuntimeError("Instala: pip install torch clip faster-whisper groq Pillow") from e


# ============================================================
# INICIALIZACIÓN DE MODELOS (singleton)
# ============================================================
def _get_clip_model():
    """Carga CLIP una sola vez y lo mantiene en memoria"""
    global _CLIP_MODEL, _CLIP_PREPROCESS
    if _CLIP_MODEL is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Cargando CLIP (ViT-B/32) en {device}...")
        _CLIP_MODEL, _CLIP_PREPROCESS = clip.load("ViT-B/32", device=device)
        logger.info("✅ CLIP listo")
    return _CLIP_MODEL, _CLIP_PREPROCESS


def _get_whisper_model():
    """Carga Whisper una sola vez y lo mantiene en memoria"""
    global _WHISPER_MODEL
    if _WHISPER_MODEL is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        compute_type = "float16" if device == "cuda" else "int8"
        logger.info(f"Cargando Whisper ({WHISPER_MODEL_SIZE}) en {device}...")
        _WHISPER_MODEL = WhisperModel(
            WHISPER_MODEL_SIZE,
            device=device,
            compute_type=compute_type,
            cpu_threads=4,
            num_workers=2
        )
        logger.info("✅ Whisper listo")
    return _WHISPER_MODEL


# ============================================================
# 1. TRANSCRIPCIÓN DE AUDIO (faster-whisper)
# ============================================================
async def transcribe_audio(file_path: str) -> str:
    """
    Transcribe un archivo de audio a texto usando Whisper.
    
    Args:
        file_path: Ruta al archivo de audio (mp3, wav, m4a, etc.)
    
    Returns:
        Texto transcrito en español
    """
    if not os.path.exists(file_path):
        logger.error(f"❌ Audio no encontrado: {file_path}")
        return ""
    
    model = _get_whisper_model()
    if not model:
        return ""
    
    try:
        loop = asyncio.get_event_loop()
        segments, _ = await loop.run_in_executor(
            None,
            lambda: model.transcribe(file_path, beam_size=5, language="es")
        )
        transcription = " ".join(segment.text for segment in segments)
        logger.info(f"✅ Transcripción completada: {len(transcription)} caracteres")
        return transcription.strip()
    except Exception as e:
        logger.exception(f"❌ Error en transcripción: {e}")
        return ""


# ============================================================
# 2. ANÁLISIS DE IMÁGENES CON CLIP (zero-shot)
# ============================================================
async def analyze_image(image_path: str, candidate_labels: List[str]) -> Dict[str, float]:
    """
    Analiza una imagen y devuelve probabilidades para cada concepto.
    
    Args:
        image_path: Ruta a la imagen
        candidate_labels: Lista de conceptos posibles (de la BD)
    
    Returns:
        Diccionario {concepto: probabilidad}
    """
    model, preprocess = _get_clip_model()
    if not model:
        return {label: 0.0 for label in candidate_labels}

    try:
        # Cargar imagen
        if not os.path.exists(image_path):
            if image_path.startswith("/static"):
                image_path = "." + image_path
            else:
                raise FileNotFoundError(f"No se encuentra {image_path}")
        
        image = Image.open(image_path).convert("RGB")
        device = next(model.parameters()).device
        image_input = preprocess(image).unsqueeze(0).to(device)

        # Preparar textos
        text_tokens = clip.tokenize(candidate_labels).to(device)

        # Calcular similitud
        with torch.no_grad():
            image_features = model.encode_image(image_input)
            text_features = model.encode_text(text_tokens)

        # Normalizar y calcular probabilidades
        image_features = image_features / image_features.norm(dim=-1, keepdim=True)
        text_features = text_features / text_features.norm(dim=-1, keepdim=True)
        similarity = (image_features @ text_features.T).squeeze(0)
        probabilities = similarity.softmax(dim=-1)

        result = {label: float(prob) for label, prob in zip(candidate_labels, probabilities)}
        best_match = max(result, key=result.get)
        logger.info(f"✅ Imagen analizada: {best_match} (confianza {result[best_match]:.2%})")
        return result
    except Exception as e:
        logger.exception(f"❌ Error analizando imagen {image_path}: {e}")
        return {label: 0.0 for label in candidate_labels}


async def analyze_multiple_images(image_paths: List[str], candidate_labels: List[str]) -> List[Dict[str, float]]:
    """Analiza varias imágenes en paralelo"""
    results = []
    for path in image_paths:
        results.append(await analyze_image(path, candidate_labels))
    return results


# ============================================================
# 3. GENERACIÓN DE DIAGNÓSTICO CON LLM (Groq API)
# ============================================================
async def generate_diagnosis(
    description: str,
    image_analysis: List[Dict[str, float]],
    transcription: Optional[str],
    vehicle_info: Optional[Dict[str, Any]],
    valid_concepts: List[str]
) -> Dict[str, Any]:
    """
    Genera un diagnóstico usando Groq API (Llama 3).
    
    Args:
        description: Descripción del problema por el usuario
        image_analysis: Resultados del análisis de imágenes con CLIP
        transcription: Transcripción del audio (si hay)
        vehicle_info: Información del vehículo
        valid_concepts: Lista de conceptos válidos de la BD
    
    Returns:
        {
            "descripcion": str,
            "nivel_confianza": float,
            "incidentes": [{"concepto": str, "nivel_confianza": float, "sugerido_por": "ia"}]
        }
    """
    if not GROQ_API_KEY or GROQ_API_KEY == "gsk_pon_tu_api_key_aqui":
        raise ValueError(
            "❌ GROQ_API_KEY no configurada. "
            "Obtén tu key en: https://console.groq.com/keys"
        )
    
    prompt = _build_prompt(description, image_analysis, transcription, vehicle_info, valid_concepts)
    
    try:
        logger.info(f"🤖 Generando diagnóstico con Groq ({GROQ_MODEL})...")
        loop = asyncio.get_event_loop()
        client = Groq(api_key=GROQ_API_KEY)
        
        response = await loop.run_in_executor(
            None,
            lambda: client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un experto mecánico automotriz. Genera diagnósticos precisos en formato JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=1000,
                top_p=0.9
            )
        )
        
        raw = response.choices[0].message.content
        logger.info(f"✅ Respuesta Groq recibida ({len(raw)} chars)")
        
        diagnosis = _parse_llm_response(raw, valid_concepts)
        diagnosis["fecha"] = datetime.utcnow()
        return diagnosis
        
    except Exception as e:
        logger.exception(f"❌ Error en Groq API: {e}")
        # Fallback de emergencia
        return {
            "descripcion": "No se pudo generar diagnóstico automático. Verifica tu GROQ_API_KEY.",
            "nivel_confianza": 0.0,
            "incidentes": []
        }


def _build_prompt(desc, img_analysis, transc, vehicle_info, valid_concepts) -> str:
    """Construye el prompt para el LLM"""
    prompt = """Eres un experto mecánico automotriz. Genera un diagnóstico en JSON.

### CONCEPTOS VÁLIDOS (solo usa estos nombres exactos):
"""
    prompt += ", ".join(valid_concepts) + "\n\n"

    prompt += "### INFORMACIÓN DEL VEHÍCULO ###\n"
    if vehicle_info:
        prompt += f"- Matrícula: {vehicle_info.get('matricula', 'N/A')}\n"
        prompt += f"- Marca/Modelo: {vehicle_info.get('marca', '')} {vehicle_info.get('modelo', '')}\n"
        prompt += f"- Año: {vehicle_info.get('anio', 'N/A')}\n"
    else:
        prompt += "No disponible.\n"

    prompt += "\n### DESCRIPCIÓN DEL CONDUCTOR ###\n"
    prompt += desc if desc else "No hay descripción.\n"

    prompt += "\n### TRANSCRIPCIÓN DE AUDIO ###\n"
    prompt += transc if transc else "No hay audio.\n"

    prompt += "\n### ANÁLISIS DE IMÁGENES (CLIP) ###\n"
    if img_analysis:
        for idx, anal in enumerate(img_analysis, 1):
            best = max(anal.items(), key=lambda x: x[1])
            prompt += f"- Imagen {idx}: {best[0]} (confianza {best[1]:.2%})\n"
    else:
        prompt += "No hay imágenes.\n"

    prompt += """
### INSTRUCCIONES ###
Genera ÚNICAMENTE un JSON válido con esta estructura:
{
    "descripcion": "texto explicativo en español del diagnóstico",
    "nivel_confianza": 0.85,
    "incidentes": [
        {"concepto": "nombre_exacto_de_la_lista", "nivel_confianza": 0.9, "sugerido_por": "ia"},
        {"concepto": "otro_concepto_de_la_lista", "nivel_confianza": 0.8, "sugerido_por": "ia"}
    ]
}

REGLAS IMPORTANTES:
- Los conceptos DEBEN estar EXACTAMENTE en la lista de conceptos válidos
- nivel_confianza general es el promedio de los niveles de los incidentes
- No incluyas texto fuera del JSON
- Si falta información, usa "informacion_insuficiente" (debe estar en la lista)

### RESPUESTA (SOLO JSON): ###
"""
    return prompt


def _parse_llm_response(raw: str, valid_concepts: List[str]) -> Dict[str, Any]:
    """Parsea y valida la respuesta del LLM"""
    import json
    import re
    
    # Extraer JSON de la respuesta
    json_match = re.search(r'\{.*\}', raw, re.DOTALL)
    if not json_match:
        logger.error("❌ No se encontró JSON en respuesta LLM")
        return {
            "descripcion": "Error de formato en respuesta IA",
            "nivel_confianza": 0.0,
            "incidentes": []
        }
    
    try:
        data = json.loads(json_match.group())
    except json.JSONDecodeError as e:
        logger.error(f"❌ JSON inválido: {e}")
        return {
            "descripcion": "Error parsing JSON",
            "nivel_confianza": 0.0,
            "incidentes": []
        }

    # Validar y filtrar incidentes
    incidentes = []
    for inc in data.get("incidentes", []):
        concepto = inc.get("concepto", "")
        if concepto not in valid_concepts:
            logger.warning(f"⚠️ Concepto '{concepto}' no es válido, se ignora")
            continue
        incidentes.append({
            "concepto": concepto,
            "nivel_confianza": min(1.0, max(0.0, float(inc.get("nivel_confianza", 0.5)))),
            "sugerido_por": "ia"
        })

    # Calcular nivel de confianza general
    if incidentes:
        nivel_general = sum(inc["nivel_confianza"] for inc in incidentes) / len(incidentes)
    else:
        nivel_general = data.get("nivel_confianza", 0.0)
    
    return {
        "descripcion": data.get("descripcion", "Diagnóstico generado por IA"),
        "nivel_confianza": float(nivel_general),
        "incidentes": incidentes
    }
