"""
Servicio de cálculo de ETA (Tiempo Estimado de Llegada).

Actualmente usa la fórmula de Haversine con velocidad promedio fija (40 km/h urbano).
Para migrar a Google Maps Routes API en el futuro, solo hay que modificar este archivo.
Ningún endpoint, modelo ni migración necesita cambios.
"""
import math
from typing import Optional


# Velocidad promedio asumida para cálculo de ETA en km/h
VELOCIDAD_PROMEDIO_KMH = 40.0


def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calcula la distancia en línea recta entre dos puntos GPS usando la fórmula de Haversine.
    Retorna la distancia en kilómetros.
    """
    R = 6371.0  # Radio de la Tierra en km

    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
    )
    c = 2 * math.asin(math.sqrt(a))

    return R * c


def calcular_eta(
    lat_origen: float,
    lon_origen: float,
    lat_destino: float,
    lon_destino: float,
    velocidad_kmh: Optional[float] = None,
) -> dict:
    """
    Calcula el ETA (Estimated Time of Arrival) entre dos coordenadas GPS.

    Args:
        lat_origen:    Latitud del técnico (punto de partida)
        lon_origen:    Longitud del técnico
        lat_destino:   Latitud del cliente (destino)
        lon_destino:   Longitud del cliente
        velocidad_kmh: Velocidad promedio en km/h (default: VELOCIDAD_PROMEDIO_KMH)

    Returns:
        dict con:
            distancia_km:  Distancia estimada en km (línea recta)
            eta_minutos:   Tiempo estimado en minutos
            metodo:        "haversine" (para transparencia con el frontend)

    Nota:
        Para migrar a Google Maps Routes API, reemplazar el cuerpo de esta
        función con una llamada HTTP a la API y retornar el mismo dict.
    """
    if velocidad_kmh is None:
        velocidad_kmh = VELOCIDAD_PROMEDIO_KMH

    distancia_km = _haversine(lat_origen, lon_origen, lat_destino, lon_destino)

    # ETA = distancia / velocidad, convertido a minutos
    eta_minutos = (distancia_km / velocidad_kmh) * 60.0

    return {
        "distancia_km": round(distancia_km, 2),
        "eta_minutos": round(eta_minutos, 1),
        "metodo": "haversine",
    }
