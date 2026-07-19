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
