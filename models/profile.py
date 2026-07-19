"""
Scr: declaración del objeto LinkProfile en el que se generan las variables de zona de Fresnel

Contrato de datos para el resultado completo del motor de cálculo.

Referencia: ARCH v1.1, §4 (models/profile.py).

``LinkProfile`` es inmutable (frozen=True). Todos los arrays físicos
obligatorios son campos no-Optional. Solo los campos del power budget
(p_rx_dbm, margin_db, availability_pct) son Optional.
"""

from dataclasses import dataclass
from typing import Optional

import numpy as np

from models.params import LinkParams
from models.terrain import TerrainData


@dataclass(frozen=True)
class LinkProfile:
    """Resultado completo de un cálculo de radioenlace.

    Arrays (longitud N = terrain.n_points):
        h_er_m [m]:      Corrección por curvatura terrestre, EQ-04.
        z_eff_m [m]:     Elevación efectiva del terreno, EQ-05.
        h_los_m [m]:     Altura de la LOS, EQ-07.
        r1_m [m]:        Radio de la primera zona de Fresnel, EQ-08.
        h_sup_m [m]:     h_LOS + r1, EQ-09.
        h_inf_m [m]:     h_LOS - r1, EQ-09.
        h_60pct_m [m]:   h_LOS - 0.6*r1, EQ-09.
        c_los_m [m]:     Despeje relativo a LOS, EQ-10.
        h_o_m [m]:       Altura de obstáculo sobre LOS, EQ-11.
        c_ffz_m [m]:     Despeje relativo al 60% de Fresnel, EQ-12.
        v [-]:           Parámetro Fresnel-Kirchhoff, EQ-13.

    Escalares:
        idx_critical:       Índice del obstáculo crítico.
        v_critical [-]:     v en el obstáculo crítico.
        g_d_db [dB]:        Coeficiente de difracción (EQ-17).
        l_d_db [dB]:        Pérdida adicional de difracción (EQ-18).
        l_fs_db [dB]:       Pérdida en espacio libre (EQ-21).

    Power budget (Optional, solo si pb_params fue proporcionado):
        p_rx_dbm [dBm]:         Potencia recibida.
        margin_db [dB]:         Margen sobre sensibilidad.
        availability_pct [%]:   Disponibilidad del enlace.
    """

    # Referencias a los datos de entrada
    params: LinkParams
    terrain: TerrainData

    # Arrays de curvatura y geometría
    h_er_m: np.ndarray
    z_eff_m: np.ndarray
    h_los_m: np.ndarray

    # Arrays de zonas de Fresnel
    r1_m: np.ndarray
    h_sup_m: np.ndarray
    h_inf_m: np.ndarray
    h_60pct_m: np.ndarray

    # Arrays de despeje y difracción
    c_los_m: np.ndarray
    h_o_m: np.ndarray
    c_ffz_m: np.ndarray
    v: np.ndarray

    # Escalares del obstáculo crítico y difracción
    idx_critical: int
    v_critical: float
    g_d_db: float
    l_d_db: float
    l_fs_db: float

    # Power budget (activable)
    p_rx_dbm: Optional[float] = None
    margin_db: Optional[float] = None
    availability_pct: Optional[float] = None
