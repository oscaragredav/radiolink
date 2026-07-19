"""
Cálculos de zonas de Fresnel y despeje (clearance).

Referencia: ARCH v1.1, §4 (core/fresnel_zones.py).
Ecuaciones: MATHSPEC v1.1, §5–§6 (EQ-08 a EQ-12).

Todas las funciones operan en unidades SI (metros).
"""

import numpy as np


def fresnel_radius_n(
    n: int,
    lam_m: float,
    d1_m: np.ndarray,
    d2_m: np.ndarray,
) -> np.ndarray:
    """Calcula el radio de la n-ésima zona de Fresnel.

    Ref: EQ-08 (MATHSPEC v1.1).

    r_n = sqrt( (n * lambda * d1 * d2) / (d1 + d2) )

    En los extremos (Tx y Rx) devuelve exactamente 0.0.

    Args:
        n [-]:      Número de la zona de Fresnel (usualmente 1).
        lam_m [m]:  Longitud de onda de la señal (c / f_Hz).
        d1_m [m]:   Distancia desde Tx a cada punto del perfil.
        d2_m [m]:   Distancia desde cada punto hasta Rx.

    Returns:
        r_n_m [m]:  Radio de la n-ésima zona de Fresnel.
    """
    d_total = d1_m + d2_m
    # Evitar división por cero
    with np.errstate(divide="ignore", invalid="ignore"):
        r_n_m = np.sqrt((n * lam_m * d1_m * d2_m) / d_total)
    
    # Manejar posibles NaNs si d_total == 0
    return np.where(d_total > 0, r_n_m, 0.0)


def fresnel_bands(
    h_los_m: np.ndarray,
    r1_m: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Calcula las bandas de Fresnel para visualización y diseño.

    Ref: EQ-09 (MATHSPEC v1.1).

    h_sup = h_LOS + r1
    h_inf = h_LOS - r1
    h_60pct = h_LOS - 0.6 * r1

    Args:
        h_los_m [m]: Altura de la línea de visión (LOS) MSL.
        r1_m [m]:    Radio de la 1ra zona de Fresnel.

    Returns:
        (h_sup_m, h_inf_m, h_60pct_m) [m MSL]: Límites superior,
        inferior y umbral crítico del 60%.
    """
    h_sup_m = h_los_m + r1_m
    h_inf_m = h_los_m - r1_m
    h_60pct_m = h_los_m - 0.6 * r1_m
    return h_sup_m, h_inf_m, h_60pct_m


def los_clearance(
    h_los_m: np.ndarray,
    z_eff_m: np.ndarray,
) -> np.ndarray:
    """Calcula el despeje relativo a la línea de visión directa (LOS).

    Ref: EQ-10 (MATHSPEC v1.1).

    C_LOS = h_LOS - z_eff

    C_LOS > 0: Despeje (terreno debajo de LOS).
    C_LOS < 0: Obstrucción (terreno sobre LOS).

    Args:
        h_los_m [m MSL]: Altura de la LOS.
        z_eff_m [m MSL]: Elevación efectiva del terreno.

    Returns:
        c_los_m [m]: Despeje respecto a LOS.
    """
    return h_los_m - z_eff_m


def obstacle_height(
    c_los_m: np.ndarray,
) -> np.ndarray:
    """Calcula la altura del obstáculo sobre la LOS.

    Ref: EQ-11 (MATHSPEC v1.1).

    h_O = -C_LOS

    h_O > 0: Obstrucción (el terreno supera la LOS).
    h_O < 0: Despeje.

    Args:
        c_los_m [m]: Despeje respecto a LOS.

    Returns:
        h_o_m [m]: Altura del obstáculo sobre LOS.
    """
    return -c_los_m


def ffz_clearance(
    c_los_m: np.ndarray,
    r1_m: np.ndarray,
) -> np.ndarray:
    """Calcula el despeje relativo al 60% de la 1ra zona de Fresnel.

    Ref: EQ-12 (MATHSPEC v1.1).

    C_FFZ = C_LOS - 0.6 * r1

    Si C_FFZ < 0, hay obstrucción del umbral crítico.

    Args:
        c_los_m [m]: Despeje respecto a LOS.
        r1_m [m]:    Radio de la 1ra zona de Fresnel.

    Returns:
        c_ffz_m [m]: Despeje relativo al 60% de Fresnel.
    """
    return c_los_m - 0.6 * r1_m
