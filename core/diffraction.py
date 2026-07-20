"""
Motor de difracción Knife-Edge.

Referencia: ARCH v1.1, §4 (core/diffraction.py).
Ecuaciones: MATHSPEC v1.1, §6–§7 (EQ-13 a EQ-18).

Todas las funciones operan en unidades SI (metros, Hz).
"""

import numpy as np
from scipy.special import fresnel as scipy_fresnel


def fresnel_kirchhoff_parameter(
    h_o_m: np.ndarray,
    lam_m: float,
    d1_m: np.ndarray,
    d2_m: np.ndarray,
) -> np.ndarray:
    """Calcula el parámetro de Fresnel-Kirchhoff v para cada punto del perfil.

    Ref: EQ-13 (MATHSPEC v1.1).

    v_i = h_O_i * sqrt( 2*(d1_i + d2_i) / (lambda * d1_i * d2_i) )

    Retorna np.nan donde d1_i == 0 o d2_i == 0 (extremos Tx y Rx).

    Convención de signo (consistente con EQ-11 y las diapositivas del profesor):
    - v > 0: obstrucción sobre la LOS.
    - v = 0: borde exactamente en la LOS.
    - v < 0: despeje por debajo de la LOS.

    Args:
        h_o_m [m]:   Altura del obstáculo sobre la LOS (EQ-11).
        lam_m [m]:   Longitud de onda (c / f_Hz).
        d1_m [m]:    Distancia desde Tx a cada punto del perfil.
        d2_m [m]:    Distancia desde cada punto hasta Rx.

    Returns:
        v [-]: Parámetro de Fresnel-Kirchhoff para cada punto.
    """
    # Crear máscara de extremos donde d1 == 0 o d2 == 0
    endpoint_mask = (d1_m == 0.0) | (d2_m == 0.0)

    # Calcular v evitando división por cero en extremos
    with np.errstate(divide="ignore", invalid="ignore"):
        d_sum = d1_m + d2_m
        d_prod = d1_m * d2_m
        v = h_o_m * np.sqrt(2.0 * d_sum / (lam_m * d_prod))

    # Forzar NaN en los extremos
    v = np.where(endpoint_mask, np.nan, v)

    return v


def critical_obstacle_index(v: np.ndarray) -> int:
    """Identifica el índice del obstáculo crítico.

    Ref: EQ-14 (MATHSPEC v1.1).

    El obstáculo crítico es el que tiene el mayor valor de v (no la mayor
    altura absoluta ni la mayor h_O). Se usa np.nanargmax para ignorar
    los NaN en los extremos.

    Args:
        v [-]: Array del parámetro de Fresnel-Kirchhoff.

    Returns:
        Índice del obstáculo crítico en el array.
    """
    return int(np.nanargmax(v))


def diffraction_function(v: float) -> complex:
    """Evalúa la función de difracción compleja F(v).

    Ref: EQ-16 (MATHSPEC v1.1).

    F(v) = (1+j)/2 * [(0.5 - C(v)) - j*(0.5 - S(v))]

    Usa scipy.special.fresnel(v), que retorna (S(v), C(v)) en ese orden.

    Verificación: F(0) = 0.5, |F(0)| = 0.5.

    Args:
        v [-]: Parámetro de Fresnel-Kirchhoff (escalar).

    Returns:
        F(v): Valor complejo de la función de difracción.
    """
    S_v, C_v = scipy_fresnel(v)

    F_v = (1.0 + 1.0j) / 2.0 * ((0.5 - C_v) - 1.0j * (0.5 - S_v))

    return complex(F_v)


def diffraction_gain_db(v: float) -> float:
    """Calcula el coeficiente de difracción G_d en dB.

    Ref: EQ-17 (MATHSPEC v1.1).

    G_d = 20 * log10(|F(v)|)

    Representa el coeficiente exacto de difracción calculado a partir
    de las integrales de Fresnel. Puede ser negativo, cero o levemente
    positivo debido al comportamiento oscilatorio de la solución exacta.

    - Para v -> -inf (despeje total): |F| -> 1, G_d -> 0 dB.
    - Para v = 0: G_d = 20*log10(0.5) = -6.0206 dB.
    - Para v > 0 creciente: G_d decrece (mayor pérdida).

    Args:
        v [-]: Parámetro de Fresnel-Kirchhoff (escalar).

    Returns:
        G_d [dB]: Coeficiente de difracción.
    """
    F_v = diffraction_function(v)
    return float(20.0 * np.log10(abs(F_v)))


def diffraction_loss_db(v: float) -> float:
    """Calcula la pérdida adicional por difracción L_d en dB.

    Ref: EQ-18 (MATHSPEC v1.1).

    L_d = max(0.0, -G_d(v))

    Retorna la pérdida adicional de difracción usada en el presupuesto
    de enlace. Nunca acredita ganancia de difracción respecto al espacio
    libre y siempre cumple L_d >= 0.

    El truncamiento a cero elimina artefactos numéricos donde |F(v)| > 1
    sin introducir ningún umbral empírico sobre v.

    Args:
        v [-]: Parámetro de Fresnel-Kirchhoff (escalar).

    Returns:
        L_d [dB]: Pérdida por difracción (siempre >= 0).
    """
    g_d = diffraction_gain_db(v)
    return max(0.0, -g_d)


def diffraction_curve(v_range: np.ndarray) -> np.ndarray:
    """Calcula G_d(v) para un array de valores v.

    Se usa para visualizar el coeficiente exacto G_d(v), no la pérdida
    truncada L_d(v).

    Args:
        v_range [-]: Array de valores del parámetro de Fresnel-Kirchhoff.

    Returns:
        g_d_db [dB]: Coeficiente de difracción para cada valor de v.
    """
    return np.array([diffraction_gain_db(float(v)) for v in v_range])
