from openai import AsyncOpenAI
import json
from typing import Optional
from app.core.config import settings
from app.schemas.ai import ResultadoDiagnosticoIA

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

async def transcribe_audio(file_path: str) -> str:
    """ Transcribe el audio enviado por el cliente usando Whisper. """
    try:
        with open(file_path, "rb") as audio_file:
            transcription = await client.audio.transcriptions.create(
                model="whisper-1", 
                file=audio_file,
                response_format="text"
            )
            return transcription
    except Exception as e:
        # Aquí se podría documentar en algún logger
        return f"Error al transcribir el audio: {str(e)}"

async def generar_diagnostico_ia(
    descripcion_texto: str, 
    imagen_url: Optional[str] = None
) -> ResultadoDiagnosticoIA:
    """ Usa multimodularidad (texto e imagen) para clasificar el incidente. """
    
    mensajes = [
        {
            "role": "system",
            "content": (
                "Eres un experto analizador de incidentes de auxilio vial. "
                "Tu trabajo es clasificar emergencias basado en texto o imagenes. "
                "Asegúrate de llenar todos los campos requeridos en el esquema indicado."
            )
        }
    ]
    
    contenido_usuario = []
    
    if descripcion_texto:
        contenido_usuario.append({"type": "text", "text": f"Descripción del cliente: {descripcion_texto}"})
        
    if imagen_url:
        contenido_usuario.append({
            "type": "image_url",
            "image_url": {"url": imagen_url, "detail": "low"}
        })
        
    if not contenido_usuario:
        contenido_usuario.append({
            "type": "text", 
            "text": "El usuario no proporcionó ninguna descripción o imagen. Indica que necesitas más información."
        })
        
    mensajes.append({
        "role": "user",
        "content": contenido_usuario
    })
    
    try:
        completion = await client.beta.chat.completions.parse(
            model="gpt-4o-mini", # Puede ser gpt-4o si se necesita mas precision
            messages=mensajes,
            response_format=ResultadoDiagnosticoIA,
        )
        
        diagnostico: ResultadoDiagnosticoIA = completion.choices[0].message.parsed
        return diagnostico
    except Exception as e:
        error_str = str(e)
        if "insufficient_quota" in error_str or "RateLimitError" in error_str or "exceeded your current quota" in error_str:
            return ResultadoDiagnosticoIA(
                categoria_sugerida="llanta",
                prioridad_sugerida="media",
                resumen_problema="[MOCK IA - CUOTA EXCEDIDA] Se detecta un problema con la llanta del vehículo basado en la descripción del conductor. Requiere asistencia en sitio.",
                nivel_confianza=0.85,
                requiere_remolque=False,
                necesita_mas_informacion=False
            )
        raise ValueError(f"No se pudo completar el análisis de IA: {str(e)}")

