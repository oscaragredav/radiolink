"""
Corrección atmosférica y curvatura terrestre.

Referencia: ARCH v1.1, §4 (core/atmosphere.py).
Ecuaciones: MATHSPEC v1.1, §2–§3 (EQ-01 a EQ-05).

Todas las funciones operan en unidades SI (metros, Hz, vatios)
salvo donde se indica explícitamente en la docstring.
"""

import numpy as np

from config.constants import R_EARTH, R_EARTH_KM


def k_from_gradient(dN_dh: float) -> float:
    """Calcula el factor de escala terrestre K a partir del gradiente dN/dh.

    Ref: EQ-03 (MATHSPEC v1.1).

    K = 1 / (1 + R_km * G * 1e-6)

    Args:
        dN_dh [N-units/km]: Gradiente de refractividad atmosférica.

    Returns:
        K [-]: Factor de escala terrestre.
    """
    return 1.0 / (1.0 + R_EARTH_KM * dN_dh * 1e-6)


def gradient_from_k(K: float) -> float:
    """Calcula el gradiente de refractividad dN/dh a partir de K.

    Ref: EQ-03 inversa (MATHSPEC v1.1).

    G = (1/K - 1) / (R_km * 1e-6)

    Args:
        K [-]: Factor de escala terrestre.

    Returns:
        dN_dh [N-units/km]: Gradiente de refractividad.
    """
    return (1.0 / K - 1.0) / (R_EARTH_KM * 1e-6)


def earth_curvature_correction(
    d1_m: np.ndarray,
    d2_m: np.ndarray,
    K: float,
) -> np.ndarray:
    """Calcula la corrección de altura por curvatura terrestre.

    Ref: EQ-04 (MATHSPEC v1.1).

    h_ER_i = (d1_i * d2_i) / (2 * K * R)

    En los extremos (d1=0 o d2=0), h_ER = 0 por definición.

    Args:
        d1_m [m]: Distancia desde Tx a cada punto del perfil.
        d2_m [m]: Distancia desde cada punto hasta Rx.
        K [-]:    Factor de escala terrestre.

    Returns:
        h_er_m [m]: Corrección por curvatura para cada punto.
    """
    return (d1_m * d2_m) / (2.0 * K * R_EARTH)


def effective_elevation(
    z_raw_m: np.ndarray,
    h_er_m: np.ndarray,
) -> np.ndarray:
    """Calcula la elevación efectiva del terreno.

    Ref: EQ-05 (MATHSPEC v1.1).

    z_eff_i = z_i + h_ER_i

    No incorpora alturas de antena. Solo terreno corregido por curvatura.

    Args:
        z_raw_m [m]:  Elevación cruda del terreno (MSL).
        h_er_m [m]:   Corrección por curvatura terrestre.

    Returns:
        z_eff_m [m]: Elevación efectiva del terreno.
    """
    return z_raw_m + h_er_m
