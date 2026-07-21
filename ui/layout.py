"""
Layout de la figura matplotlib para el evaluador de radioenlace.

Define la figura (14×10 pulgadas), los ejes de los tres paneles y
las regiones reservadas para widgets (sliders y botones).

Referencia: ARCH v1.1, §7.

No importa ningún módulo de core/. Solo matplotlib.
"""

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.axes import Axes


# Colores de la paleta (ARCH §7)
COLOR_LOS_A = "#E63946"
COLOR_FRESNEL_A = "#4895EF"
COLOR_FRESNEL_60_A = "#4895EF"
COLOR_OBSTACLE = "#F4A261"
COLOR_TERRAIN_RAW = "#AAAAAA"
COLOR_TERRAIN_EFF = "#333333"
COLOR_MAST = "#333333"
COLOR_GD_CURVE = "#555555"
COLOR_V_ZERO = "#CC0000"


def build_figure() -> tuple[Figure, Axes, Axes, Axes]:
    """Construye la figura y los tres paneles.

    Layout (14×10 pulgadas, 140 dpi):
        - ax_terrain: panel superior, perfil completo.
        - ax_diffraction: panel inferior izquierdo, curva Gd(v).
        - ax_results: panel inferior derecho, tabla de resultados.
        - Zona inferior reservada para widgets (sliders y botones).

    Returns:
        fig, ax_terrain, ax_diffraction, ax_results
    """
    fig = plt.figure(figsize=(14, 10), dpi=140)
    fig.patch.set_facecolor("#1A1A2E")

    # Márgenes generales
    left = 0.06
    right = 0.97
    top = 0.96
    widget_top = 0.18   # zona inferior reservada para widgets en Etapa 8
    mid_v = widget_top + 0.02  # separación inferior de los paneles secundarios
    split_v = mid_v + 0.28     # altura total de los paneles secundarios

    # Separación horizontal entre difracción y resultados
    h_split = 0.50
    gap = 0.02

    # Panel superior: terreno
    ax_terrain = fig.add_axes(
        [left, split_v + 0.04, right - left, top - split_v - 0.04]
    )

    # Panel inferior izquierdo: difracción
    ax_diffraction = fig.add_axes(
        [left, mid_v, h_split - left - gap, split_v - mid_v]
    )

    # Panel inferior derecho: resultados
    ax_results = fig.add_axes(
        [h_split + gap, mid_v, right - h_split - gap, split_v - mid_v]
    )

    for ax in (ax_terrain, ax_diffraction, ax_results):
        ax.set_facecolor("#0D1117")
        for spine in ax.spines.values():
            spine.set_edgecolor("#30363D")
        ax.tick_params(colors="#8B949E", labelsize=8)
        ax.xaxis.label.set_color("#8B949E")
        ax.yaxis.label.set_color("#8B949E")
        ax.title.set_color("#C9D1D9")

    return fig, ax_terrain, ax_diffraction, ax_results
