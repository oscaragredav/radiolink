"""
Layout de la figura matplotlib para el evaluador de radioenlace.

Define la figura (14×10 pulgadas), los ejes de los tres paneles de datos
y los ejes de los widgets interactivos (sliders y botones).

Referencia: ARCH v1.1, §7.

No importa ningún módulo de core/. Solo matplotlib.
"""

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from dataclasses import dataclass

# ---------------------------------------------------------------------------
# Paleta de colores (ARCH §7)
# ---------------------------------------------------------------------------

COLOR_LOS_A = "#E63946"
COLOR_FRESNEL_A = "#4895EF"
COLOR_FRESNEL_60_A = "#4895EF"
COLOR_OBSTACLE = "#F4A261"
COLOR_TERRAIN_RAW = "#AAAAAA"
COLOR_TERRAIN_EFF = "#333333"
COLOR_MAST = "#333333"
COLOR_GD_CURVE = "#555555"
COLOR_V_ZERO = "#CC0000"

# Colores de widgets
COLOR_WIDGET_BG = "#161B22"
COLOR_WIDGET_FACE = "#21262D"
COLOR_WIDGET_TEXT = "#C9D1D9"
COLOR_SLIDER_COLOR = "#4895EF"
COLOR_BTN_FACE = "#238636"
COLOR_BTN_HOVER = "#2EA043"

# ---------------------------------------------------------------------------
# Constantes de layout
# ---------------------------------------------------------------------------

#  Zona inferior total para widgets
_WIDGET_ZONE_BOTTOM = 0.01
_WIDGET_ZONE_TOP = 0.18

# Sliders: posición y dimensiones [left, bottom, width, height]
_SLIDER_LEFT = 0.10
_SLIDER_WIDTH = 0.50
_SLIDER_H = 0.025
_SLIDER_GAP = 0.008

# Posición base del primer slider (desde arriba de la zona de widgets)
_S1_BOTTOM = _WIDGET_ZONE_TOP - _SLIDER_H - 0.005
_S2_BOTTOM = _S1_BOTTOM - _SLIDER_H - _SLIDER_GAP
_S3_BOTTOM = _S2_BOTTOM - _SLIDER_H - _SLIDER_GAP
_S4_BOTTOM = _S3_BOTTOM - _SLIDER_H - _SLIDER_GAP

# Botones
_BTN_LEFT = 0.67
_BTN_WIDTH = 0.08
_BTN_H = 0.035
_BTN_GAP = 0.010
_BTN_ROW1 = _S2_BOTTOM
_BTN_ROW2 = _BTN_ROW1 - _BTN_H - _BTN_GAP

# Toggle terrain crudo/efectivo
_TOGGLE_LEFT = 0.67
_TOGGLE_BOTTOM = _BTN_ROW2 - _BTN_H - _BTN_GAP
_TOGGLE_WIDTH = 0.10
_TOGGLE_H = 0.04


@dataclass
class WidgetAxes:
    """Colección de Axes destinados a alojar widgets matplotlib."""
    ax_slider_freq: Axes
    ax_slider_k: Axes
    ax_slider_htx: Axes
    ax_slider_hrx: Axes
    ax_btn_v1: Axes
    ax_btn_v2: Axes
    ax_btn_v3: Axes
    ax_toggle_raw: Axes

def build_figure() -> tuple[Figure, Axes, Axes, Axes]:
    """Construye la figura y los tres paneles de datos.
    Layout (14×10 pulgadas, 140 dpi):
        - ax_terrain:      Panel superior — perfil completo.
        - ax_diffraction:  Panel inferior izquierdo — curva Gd(v).
        - ax_results:      Panel inferior derecho — tabla numérica.
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
        
    # Bottom of lower panels (0.26 gives a 0.08 gap above widgets at 0.18)
    mid_v = 0.26
    # Top of lower panels
    split_v = mid_v + 0.24
    # Bottom of top panel (gives a 0.08 gap above lower panels)
    terrain_bottom = split_v + 0.08

    h_split = 0.50
    gap = 0.02

    # Panel superior: terreno
    ax_terrain = fig.add_axes(
        [left, terrain_bottom, right - left, top - terrain_bottom]
    )

    # Panel inferior izquierdo: difracción
    ax_diffraction = fig.add_axes(
        [left, mid_v, h_split - left - gap, split_v - mid_v]
    )

    # Panel inferior derecho: resultados
    ax_results = fig.add_axes(
        [h_split + gap, mid_v, right - h_split - gap, split_v - mid_v]
    )

    _style_data_axes(ax_terrain, ax_diffraction, ax_results)
    return fig, ax_terrain, ax_diffraction, ax_results
def build_widget_axes(fig: Figure) -> WidgetAxes:
    """Crea los Axes para los widgets interactivos.
    Debe llamarse después de build_figure(), pasando la misma Figure.
    Los Axes resultantes se usan directamente por matplotlib.widgets.
    Args:
        fig: Figure devuelta por build_figure().
    Returns:
        WidgetAxes con todos los Axes de widgets.
    """
    # ---- Sliders ----
    ax_slider_freq = fig.add_axes(
        [_SLIDER_LEFT, _S1_BOTTOM, _SLIDER_WIDTH, _SLIDER_H],
        facecolor=COLOR_WIDGET_FACE,
    )
    ax_slider_k = fig.add_axes(
        [_SLIDER_LEFT, _S2_BOTTOM, _SLIDER_WIDTH, _SLIDER_H],
        facecolor=COLOR_WIDGET_FACE,
    )
    ax_slider_htx = fig.add_axes(
        [_SLIDER_LEFT, _S3_BOTTOM, _SLIDER_WIDTH, _SLIDER_H],
        facecolor=COLOR_WIDGET_FACE,
    )
    ax_slider_hrx = fig.add_axes(
        [_SLIDER_LEFT, _S4_BOTTOM, _SLIDER_WIDTH, _SLIDER_H],
        facecolor=COLOR_WIDGET_FACE,
    )
    # ---- Botones de casos ----
    ax_btn_v1 = fig.add_axes(
        [_BTN_LEFT, _BTN_ROW1, _BTN_WIDTH, _BTN_H],
        facecolor=COLOR_WIDGET_FACE,
    )
    ax_btn_v2 = fig.add_axes(
        [_BTN_LEFT + _BTN_WIDTH + _BTN_GAP, _BTN_ROW1, _BTN_WIDTH, _BTN_H],
        facecolor=COLOR_WIDGET_FACE,
    )
    ax_btn_v3 = fig.add_axes(
        [_BTN_LEFT + 2 * (_BTN_WIDTH + _BTN_GAP), _BTN_ROW1, _BTN_WIDTH, _BTN_H],
        facecolor=COLOR_WIDGET_FACE,
    )
    # ---- Toggle terreno crudo/efectivo ----
    ax_toggle_raw = fig.add_axes(
        [_TOGGLE_LEFT, _TOGGLE_BOTTOM, _TOGGLE_WIDTH, _TOGGLE_H],
        facecolor=COLOR_WIDGET_FACE,
    )
    return WidgetAxes(
        ax_slider_freq=ax_slider_freq,
        ax_slider_k=ax_slider_k,
        ax_slider_htx=ax_slider_htx,
        ax_slider_hrx=ax_slider_hrx,
        ax_btn_v1=ax_btn_v1,
        ax_btn_v2=ax_btn_v2,
        ax_btn_v3=ax_btn_v3,
        ax_toggle_raw=ax_toggle_raw,
    )
# ---------------------------------------------------------------------------
# Helpers internos
# ---------------------------------------------------------------------------
def _style_data_axes(*axes: Axes) -> None:
    """Aplica el estilo oscuro a los Axes de datos."""
    for ax in axes:
        ax.set_facecolor("#0D1117")
        for spine in ax.spines.values():
            spine.set_edgecolor("#30363D")
        ax.tick_params(colors="#8B949E", labelsize=8)
        ax.xaxis.label.set_color("#8B949E")
        ax.yaxis.label.set_color("#8B949E")
        ax.title.set_color("#C9D1D9")
