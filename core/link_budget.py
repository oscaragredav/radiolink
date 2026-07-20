"""
Presupuesto de enlace (link budget).

Referencia: ARCH v1.1, §4 (core/link_budget.py).
Ecuaciones: MATHSPEC v1.1, §8–§10 (EQ-20 a EQ-24).

Todas las funciones operan en unidades SI (metros, Hz, dB, dBm).
"""

import numpy as np

from config.constants import C_LIGHT
from models.params import LinkParams, PowerBudgetParams


def free_space_loss_db(d_total_m: float, f_hz: float) -> float:
    """Calcula la pérdida en espacio libre (Friis) en dB.

    Ref: EQ-21 (MATHSPEC v1.1).

    L_fs [dB] = 20 * log10(4 * pi * d_T / lambda)

    Usa la forma SI fundamental con distancia en metros y frecuencia
    en Hz. Equivalente a la forma numérica:
    L_fs = 92.45 + 20*log10(f_GHz) + 20*log10(d_km)

    Args:
        d_total_m [m]:  Distancia total Tx–Rx.
        f_hz [Hz]:      Frecuencia de operación.

    Returns:
        L_fs [dB]: Pérdida en espacio libre.
    """
    lam_m = C_LIGHT / f_hz
    return float(20.0 * np.log10(4.0 * np.pi * d_total_m / lam_m))


def received_power_dbm(
    params: LinkParams,
    pb: PowerBudgetParams,
    l_fs_db: float,
    l_d_db: float,
) -> float:
    """Calcula la potencia recibida en dBm.

    Ref: EQ-22 (MATHSPEC v1.1).

    P_Rx = P_Tx + G_Tx - L_c,Tx - L_fs - L_d + G_Rx - L_c,Rx

    Args:
        params:     Parámetros del enlace (LinkParams).
        pb:         Parámetros del presupuesto (PowerBudgetParams).
        l_fs_db [dB]:  Pérdida en espacio libre.
        l_d_db [dB]:   Pérdida adicional por difracción.

    Returns:
        P_Rx [dBm]: Potencia recibida.
    """
    return float(
        pb.p_tx_dbm
        + pb.g_tx_dbi
        - pb.l_cable_tx_db
        - l_fs_db
        - l_d_db
        + pb.g_rx_dbi
        - pb.l_cable_rx_db
    )


def link_margin_db(
    p_rx_dbm: float,
    sensitivity_dbm: float,
) -> float:
    """Calcula el margen de enlace (fade margin).

    Ref: EQ-23 (MATHSPEC v1.1).

    F [dB] = P_Rx - S

    El enlace es viable si F > 0 dB.

    Args:
        p_rx_dbm [dBm]:       Potencia recibida.
        sensitivity_dbm [dBm]: Sensibilidad del receptor.

    Returns:
        F [dB]: Margen de enlace.
    """
    return float(p_rx_dbm - sensitivity_dbm)


def link_availability(
    margin_db: float,
    f_ghz: float,
    d_km: float,
    a: float,
    b: float,
) -> float:
    """Calcula la disponibilidad del enlace sin diversidad espacial.

    Ref: EQ-24 (MATHSPEC v1.1).

    A = (1 - a * b * 10.42e-6 * f_GHz * d_km^3 * 10^(-F/10)) * 100 %

    Args:
        margin_db [dB]:  Margen de enlace (fade margin).
        f_ghz [GHz]:     Frecuencia de operación en GHz.
        d_km [km]:       Distancia total en km.
        a [-]:           Factor de clima (0.25–1.0).
        b [-]:           Factor de terreno (0.25–4.0).

    Returns:
        A [%]: Disponibilidad del enlace (0–100).
    """
    outage_factor = (
        a * b * 10.42e-6 * f_ghz * (d_km ** 3) * (10.0 ** (-margin_db / 10.0))
    )
    return float((1.0 - outage_factor) * 100.0)
