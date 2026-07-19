"""
Carga y serialización de perfiles de terreno CSV.

Referencia: ARCH v1.1, §4 y §8 (data/loader.py).

El formato CSV esperado tiene las columnas:
    distance_m, latitude, longitude, elevation_m
"""

import numpy as np
import pandas as pd

from models.terrain import TerrainData


class TerrainLoadError(Exception):
    """Error de validación al cargar un perfil de terreno."""

    pass


def load_terrain_csv(filepath: str) -> TerrainData:
    """Lee un CSV de perfil de terreno y retorna un TerrainData validado.

    Validaciones (ARCH §8):
        - El CSV contiene al menos 50 puntos.
        - distance_m[0] es exactamente 0.0.
        - distance_m es estrictamente creciente.
        - elevation_m no contiene NaN.

    Args:
        filepath: Ruta al archivo CSV.

    Returns:
        TerrainData con los arrays del perfil.

    Raises:
        TerrainLoadError: Si alguna validación falla.
    """
    try:
        df = pd.read_csv(filepath)
    except Exception as e:
        raise TerrainLoadError(f"No se pudo leer el archivo CSV: {e}") from e

    # Verificar columnas requeridas
    required_columns = {"distance_m", "latitude", "longitude", "elevation_m"}
    missing = required_columns - set(df.columns)
    if missing:
        raise TerrainLoadError(
            f"Columnas faltantes en el CSV: {missing}. "
            f"Se requieren: {required_columns}"
        )

    # Validar mínimo de 50 puntos
    if len(df) < 50:
        raise TerrainLoadError(
            f"El perfil debe contener al menos 50 puntos, "
            f"pero tiene {len(df)}."
        )

    distance_m = df["distance_m"].values.astype(float)
    latitude = df["latitude"].values.astype(float)
    longitude = df["longitude"].values.astype(float)
    elevation_m = df["elevation_m"].values.astype(float)

    # Validar distance_m[0] == 0.0
    if distance_m[0] != 0.0:
        raise TerrainLoadError(
            f"distance_m[0] debe ser exactamente 0.0, "
            f"pero es {distance_m[0]}."
        )

    # Validar distancias crecientes estrictamente
    diffs = np.diff(distance_m) #calcula la diferencia entre cada punto consecutivo
    if not np.all(diffs > 0):
        raise TerrainLoadError(
            "distance_m debe ser estrictamente creciente. "
            "Se encontraron valores no monótonos."
        )

    # Validar sin NaN en elevation_m
    if np.any(np.isnan(elevation_m)):
        raise TerrainLoadError(
            "elevation_m contiene valores NaN. "
            "Todos los puntos deben tener elevación definida."
        )

    return TerrainData(
        d1_m=distance_m,
        lat=latitude,
        lon=longitude,
        elevation_m=elevation_m,
        source=filepath,
    )


def save_terrain_csv(terrain: TerrainData, filepath: str) -> None:
    """Serializa TerrainData al formato CSV estándar.

    Args:
        terrain: Datos de terreno a guardar.
        filepath: Ruta de destino del archivo CSV.
    """
    df = pd.DataFrame(
        {
            "distance_m": terrain.d1_m,
            "latitude": terrain.lat,
            "longitude": terrain.lon,
            "elevation_m": terrain.elevation_m,
        }
    )
    df.to_csv(filepath, index=False)
