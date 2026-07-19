"""
Casos de validación predefinidos.

Referencia: ARCH v1.1, §4 (validation/cases.py).
"""

from data.loader import load_terrain_csv
from models.params import LinkParams
from models.terrain import TerrainData


def case_flat_earth() -> tuple[TerrainData, LinkParams]:
    """
    Caso V-1: perfil plano de 10 km.
    """
    terrain = load_terrain_csv("data/profiles/validation_flat.csv")
    params = LinkParams(
        f_hz=7e9,
        h_tx_m=14.64,
        h_rx_m=14.64,
        K=1e12,
    )
    return terrain, params


def case_edge_on_los(
    d1_m: float = 4_000,
    d2_m: float = 6_000,
    f_hz: float = 7e9,
) -> tuple[TerrainData, LinkParams]:
    """
    Caso V-2: borde exactamente sobre la LOS.
    """
    terrain = load_terrain_csv("data/profiles/validation_edge.csv")
    params = LinkParams(
        f_hz=f_hz,
        h_tx_m=10.0,
        h_rx_m=10.0,
        K=1e12,
    )
    return terrain, params


def case_lima() -> tuple[TerrainData, LinkParams]:
    """
    Caso V-3: carga data/profiles/lima_atocongo.csv.
    """
    terrain = load_terrain_csv("data/profiles/lima_atocongo.csv")
    params = LinkParams(
        f_hz=7e9,
        h_tx_m=10.0,
        h_rx_m=10.0,
        K=4 / 3,
    )
    return terrain, params
