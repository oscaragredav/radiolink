"""Cliente HTTP para perfiles topográficos entre dos coordenadas."""
from __future__ import annotations

import numpy as np
import requests

from models.terrain import TerrainData

API_URL = "https://api.opentopodata.org/v1/srtm90m"


class TerrainAPIError(Exception):
    """La API no pudo entregar un perfil topográfico válido."""


def _haversine_m(lat1, lon1, lat2, lon2) -> np.ndarray:
    radius_m = 6_371_000.0
    p1, p2 = np.radians(lat1), np.radians(lat2)
    dp = p2 - p1
    dl = np.radians(lon2) - np.radians(lon1)
    a = np.sin(dp / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dl / 2) ** 2
    return 2 * radius_m * np.arctan2(np.sqrt(a), np.sqrt(1 - a))


def fetch_terrain_profile(tx_lat: float, tx_lon: float,
                          rx_lat: float, rx_lon: float,
                          *, n_points: int = 100,
                          timeout: float = 15.0) -> TerrainData:
    """Descarga elevaciones SRTM90m para puntos equiespaciados del enlace."""
    coords = (tx_lat, tx_lon, rx_lat, rx_lon)
    if not all(np.isfinite(coords)) or not (-90 <= tx_lat <= 90) or not (-90 <= rx_lat <= 90):
        raise TerrainAPIError("Coordenadas inválidas")
    if not (-180 <= tx_lon <= 180) or not (-180 <= rx_lon <= 180):
        raise TerrainAPIError("Coordenadas inválidas")
    if n_points < 50 or (tx_lat == rx_lat and tx_lon == rx_lon):
        raise TerrainAPIError("El enlace debe contener al menos 50 puntos y tener longitud positiva")

    lat = np.linspace(tx_lat, rx_lat, n_points)
    lon = np.linspace(tx_lon, rx_lon, n_points)
    locations = "|".join(f"{la:.7f},{lo:.7f}" for la, lo in zip(lat, lon))
    try:
        response = requests.get(API_URL, params={"locations": locations},
                                timeout=timeout)
        response.raise_for_status()
        payload = response.json()
        results = payload["results"]
        elevation = np.asarray([item["elevation"] for item in results], dtype=float)
    except (requests.RequestException, ValueError, KeyError, TypeError) as exc:
        raise TerrainAPIError("No se pudo conectar a la API") from exc

    if len(elevation) != n_points or not np.all(np.isfinite(elevation)):
        raise TerrainAPIError("La API devolvió un perfil incompleto")
    segments = _haversine_m(lat[:-1], lon[:-1], lat[1:], lon[1:])
    distance = np.concatenate(([0.0], np.cumsum(segments)))
    return TerrainData(distance, lat, lon, elevation, source=API_URL)
