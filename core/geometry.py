"""
Geometría del enlace: alturas de antena y línea de visión directa.

Referencia: ARCH v1.1, §4 (core/geometry.py).
Ecuaciones: MATHSPEC v1.1, §4 (EQ-06, EQ-07).

Todas las funciones operan en unidades SI (metros).
"""

import numpy as np


def antenna_heights_msl(
    z_tx_m: float,
    h_tx_m: float,
    z_rx_m: float,
    h_rx_m: float,
) -> tuple[float, float]:
    """Calcula las alturas absolutas de antena sobre el nivel del mar.

    Ref: EQ-06 (MATHSPEC v1.1).

    H_Tx = z_Tx + h_Tx
    H_Rx = z_Rx + h_Rx

    donde z_Tx y z_Rx son las elevaciones del terreno en los extremos.

    Args:
        z_tx_m [m]: Elevación del terreno en Tx (MSL).
        h_tx_m [m]: Altura del mástil en Tx.
        z_rx_m [m]: Elevación del terreno en Rx (MSL).
        h_rx_m [m]: Altura del mástil en Rx.

    Returns:
        (H_tx_m, H_rx_m) [m MSL]: Alturas absolutas de antena.
    """
    H_tx_m = z_tx_m + h_tx_m
    H_rx_m = z_rx_m + h_rx_m
    return H_tx_m, H_rx_m


def los_height(
    H_tx_m: float,
    H_rx_m: float,
    d1_m: np.ndarray,
    d_total_m: float,
) -> np.ndarray:
    """Calcula la altura de la línea de visión directa en cada punto.

    Ref: EQ-07 (MATHSPEC v1.1).

    h_LOS_i = H_Tx + (H_Rx - H_Tx) * (d1_i / d_T)

    La LOS es la interpolación lineal entre H_Tx y H_Rx sobre la
    distancia total del trayecto.

    Args:
        H_tx_m [m MSL]:    Altura absoluta de la antena Tx.
        H_rx_m [m MSL]:    Altura absoluta de la antena Rx.
        d1_m [m]:          Distancia desde Tx a cada punto.
        d_total_m [m]:     Distancia total Tx–Rx.

    Returns:
        h_los_m [m MSL]: Altura de la LOS en cada punto.
    """
    return H_tx_m + (H_rx_m - H_tx_m) * (d1_m / d_total_m)
