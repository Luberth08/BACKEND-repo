from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum

class CategoriaIAEnum(str, Enum):
    bateria = "bateria"
    llanta = "llanta"
    choque = "choque"
    motor = "motor"
    otros = "otros"
    incierto = "incierto"

class PrioridadIAEnum(str, Enum):
    baja = "baja"
    media = "media"
    alta = "alta"
    critica = "critica"
    emergencia = "emergencia"

class ResultadoDiagnosticoIA(BaseModel):
    categoria_sugerida: CategoriaIAEnum = Field(..., description="Categoría principal del incidente identificada")
    prioridad_sugerida: PrioridadIAEnum = Field(..., description="Prioridad calculada para el incidente")
    resumen_problema: str = Field(..., description="Ficha o resumen amigable estructurado sobre el incidente detectado")
    nivel_confianza: float = Field(..., ge=0.0, le=1.0, description="Grado de certeza del modelo IA sobre la respuesta generada")
    requiere_remolque: bool = Field(..., description="Si el análisis visual/auditivo sugiere que el vehículo necesita remolque")
    necesita_mas_informacion: bool = Field(default=False, description="True si la solicitud es ambigua y se necesita información adicional")
