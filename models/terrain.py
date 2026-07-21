"""
Contrato de datos para el perfil de terreno.

Referencia: ARCH v1.1, §4 (models/terrain.py).

``elevation_m`` contiene exclusivamente elevación de terreno sobre el
nivel medio del mar. Nunca contiene alturas de antena.
"""

from dataclasses import dataclass

import numpy as np


@dataclass
class TerrainData:
    """Perfil de terreno entre Tx y Rx.

    Atributos:
        d1_m [m]:           Distancias acumuladas desde Tx.
        lat [-]:            Latitudes de cada punto.
        lon [-]:            Longitudes de cada punto.
        elevation_m [m]:    Elevación del terreno (MSL).
        source:             Identificador del origen de los datos.
    """

    d1_m: np.ndarray
    lat: np.ndarray
    lon: np.ndarray
    elevation_m: np.ndarray
    source: str
    is_synthetic: bool = False

    @property
    def d_total_m(self) -> float:
        """Distancia total Tx–Rx [m]."""
        return float(self.d1_m[-1])

    @property
    def d2_m(self) -> np.ndarray:
        """Distancia desde cada punto hasta Rx [m]."""
        return self.d_total_m - self.d1_m

    @property
    def n_points(self) -> int:
        """Número de puntos del perfil."""
        return len(self.d1_m)


def synthetic_obstacle_terrain(d_total_km: float, d_obs_km: float,
                               z_obs_m: float,
                               n_points: int = 201) -> TerrainData:
    """Crea un perfil plano con un único knife-edge móvil interior."""
    d_total_m = float(d_total_km) * 1_000.0
    d_obs_m = float(d_obs_km) * 1_000.0
    if not 1.0 <= d_total_km <= 50.0:
        raise ValueError("d_total debe estar entre 1 y 50 km")
    if not 100.0 <= d_obs_m <= d_total_m - 100.0:
        raise ValueError("d_obs debe quedar al menos a 0.1 km de los extremos")
    if not 0.0 <= z_obs_m <= 300.0:
        raise ValueError("z_obs debe estar entre 0 y 300 m")

    # Se inserta d_obs exactamente para que el marcador nunca se desfase.
    base = np.linspace(0.0, d_total_m, n_points)
    distance = np.unique(np.append(base, d_obs_m))
    elevation = np.zeros_like(distance)
    elevation[np.searchsorted(distance, d_obs_m)] = float(z_obs_m)
    nan_coords = np.full_like(distance, np.nan)
    return TerrainData(distance, nan_coords.copy(), nan_coords, elevation,
                       source="synthetic:mobile-obstacle", is_synthetic=True)
