"""Layout de la interfaz comparativa de RadioLink LOS (Etapa 9)."""

from dataclasses import dataclass
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure

COLOR_LOS_A = "#E63946"
COLOR_LOS_B = "#2DD4BF"
COLOR_FRESNEL_A = "#4895EF"
COLOR_FRESNEL_B = "#A78BFA"
COLOR_FRESNEL_60_A = COLOR_FRESNEL_A
COLOR_OBSTACLE = "#F4A261"
COLOR_OBSTACLE_B = "#2DD4BF"
COLOR_TERRAIN_RAW = "#AAAAAA"
COLOR_TERRAIN_EFF = "#333333"
COLOR_MAST = "#333333"
COLOR_GD_CURVE = "#777777"
COLOR_V_ZERO = "#CC0000"
COLOR_WIDGET_FACE = "#2E3440"
COLOR_WIDGET_EDGE = "#5E81AC"
COLOR_WIDGET_TEXT = "#ECEFF4"
COLOR_SLIDER_COLOR = "#4895EF"
COLOR_BTN_FACE = "#2E3440"
COLOR_BTN_HOVER = "#434C5E"


@dataclass
class WidgetAxes:
    ax_slider_freq: Axes
    ax_slider_k: Axes
    ax_slider_htx: Axes
    ax_slider_hrx: Axes
    ax_slider_htx_b: Axes
    ax_slider_hrx_b: Axes
    ax_btn_v1: Axes
    ax_btn_v2: Axes
    ax_btn_v3: Axes
    ax_btn_api: Axes
    ax_toggle_mobile: Axes
    ax_toggle_raw: Axes
    ax_toggle_design_b: Axes
    ax_toggle_power_budget: Axes
    ax_slider_ptx: Axes
    ax_slider_gtx: Axes
    ax_slider_grx: Axes
    ax_slider_sensitivity: Axes
    ax_slider_d_total: Axes
    ax_slider_d_obs: Axes
    ax_slider_z_obs: Axes


def build_figure() -> tuple[Figure, Axes, Axes, Axes]:
    fig = plt.figure(figsize=(14, 10), dpi=140)
    grid = fig.add_gridspec(2, 2, height_ratios=(1.35, 1.0))
    fig.patch.set_facecolor("#1A1A2E")
    ax_terrain = fig.add_subplot(grid[0, :])
    ax_diffraction = fig.add_subplot(grid[1, 0])
    ax_results = fig.add_subplot(grid[1, 1])
    # Y < 0.22 queda íntegramente reservada para widgets.
    fig.subplots_adjust(bottom=0.26, hspace=0.40, wspace=0.25)
    _style_data_axes(ax_terrain, ax_diffraction, ax_results)
    return fig, ax_terrain, ax_diffraction, ax_results


def _widget_axis(fig: Figure, box: list[float]) -> Axes:
    ax = fig.add_axes(box, facecolor=COLOR_WIDGET_FACE)
    for spine in ax.spines.values():
        spine.set_edgecolor(COLOR_WIDGET_EDGE)
    return ax


def build_widget_axes(fig: Figure) -> WidgetAxes:
    h = 0.022
    ys = (0.185, 0.142, 0.099, 0.056)
    # Se deja espacio dentro de cada rango para label y valor del Slider.
    left = [_widget_axis(fig, [0.14, y, 0.20, h]) for y in ys]
    centre = [_widget_axis(fig, [0.48, y, 0.11, h]) for y in ys[:2]]
    return WidgetAxes(
        ax_slider_freq=left[0], ax_slider_k=left[1],
        ax_slider_htx=left[2], ax_slider_hrx=left[3],
        ax_slider_htx_b=centre[0], ax_slider_hrx_b=centre[1],
        # Zona derecha: presets arriba; opciones siempre visibles al costado.
        ax_btn_v1=_widget_axis(fig, [0.68, 0.185, 0.060, 0.032]),
        ax_btn_v2=_widget_axis(fig, [0.75, 0.185, 0.060, 0.032]),
        ax_btn_v3=_widget_axis(fig, [0.82, 0.185, 0.060, 0.032]),
        ax_btn_api=_widget_axis(fig, [0.89, 0.185, 0.095, 0.032]),
        ax_toggle_mobile=_widget_axis(fig, [0.875, 0.057, 0.110, 0.032]),
        ax_toggle_raw=_widget_axis(fig, [0.875, 0.018, 0.110, 0.032]),
        ax_toggle_design_b=_widget_axis(fig, [0.875, 0.135, 0.110, 0.032]),
        ax_toggle_power_budget=_widget_axis(fig, [0.875, 0.096, 0.110, 0.032]),
        # Power Budget ocupa su propia subcolumna derecha.
        ax_slider_ptx=_widget_axis(fig, [0.70, 0.137, 0.145, 0.016]),
        ax_slider_gtx=_widget_axis(fig, [0.70, 0.104, 0.145, 0.016]),
        ax_slider_grx=_widget_axis(fig, [0.70, 0.071, 0.145, 0.016]),
        ax_slider_sensitivity=_widget_axis(fig, [0.70, 0.038, 0.145, 0.016]),
        # Posiciones base del móvil; App las sube cuando Diseño B está OFF.
        ax_slider_d_total=_widget_axis(fig, [0.48, 0.099, 0.11, 0.018]),
        ax_slider_d_obs=_widget_axis(fig, [0.48, 0.062, 0.11, 0.018]),
        ax_slider_z_obs=_widget_axis(fig, [0.48, 0.025, 0.11, 0.018]),
    )


def _style_data_axes(*axes: Axes) -> None:
    for ax in axes:
        ax.set_facecolor("#0D1117")
        for spine in ax.spines.values():
            spine.set_edgecolor("#30363D")
        ax.tick_params(colors="#8B949E", labelsize=8)
        ax.xaxis.label.set_color("#8B949E")
        ax.yaxis.label.set_color("#8B949E")
        ax.title.set_color("#C9D1D9")
