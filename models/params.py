"""
Contratos de datos para parámetros del enlace.

Referencia: ARCH v1.1, §4 (models/params.py).

Ambas clases son inmutables (frozen=True). Para modificar parámetros
usar exclusivamente ``dataclasses.replace()``.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class LinkParams:
    """Parámetros geométricos y atmosféricos del enlace.

    Atributos:
        f_hz [Hz]:      Frecuencia de operación.
        h_tx_m [m]:     Altura del mástil en Tx.
        h_rx_m [m]:     Altura del mástil en Rx.
        K [-]:          Factor de escala terrestre efectivo.
    """

    f_hz: float
    h_tx_m: float
    h_rx_m: float
    K: float


@dataclass(frozen=True)
class PowerBudgetParams:
    """Parámetros del presupuesto de enlace.

    Atributos:
        p_tx_dbm [dBm]:          Potencia de transmisión.
        g_tx_dbi [dBi]:          Ganancia de antena Tx.
        g_rx_dbi [dBi]:          Ganancia de antena Rx.
        l_cable_tx_db [dB]:      Pérdida de cable/feeder en Tx.
        l_cable_rx_db [dB]:      Pérdida de cable/feeder en Rx.
        sensitivity_dbm [dBm]:   Sensibilidad del receptor.
        a_climate [-]:           Factor de clima (0.25–1.0).
        b_terrain [-]:           Factor de terreno (0.25–4.0).
    """

    p_tx_dbm: float
    g_tx_dbi: float
    g_rx_dbi: float
    l_cable_tx_db: float
    l_cable_rx_db: float
    sensitivity_dbm: float
    a_climate: float
    b_terrain: float
