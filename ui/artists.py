"""
Caché de artistas matplotlib para los tres paneles.
Crea los objetos Line2D, PolyCollection y Text una única vez
y los expone como campos para que los paneles los actualicen
mediante set_data / set_xy sin llamar a ax.clear().
Referencia: ARCH v1.1, §7.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING
import numpy as np
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
from matplotlib.axes import Axes
from matplotlib.collections import PolyCollection
from matplotlib.lines import Line2D
from matplotlib.text import Text
from ui.layout import (
    COLOR_LOS_A,
    COLOR_FRESNEL_A,
    COLOR_FRESNEL_60_A,
    COLOR_OBSTACLE,
    COLOR_TERRAIN_RAW,
    COLOR_TERRAIN_EFF,
    COLOR_MAST,
    COLOR_GD_CURVE,
    COLOR_V_ZERO,
    COLOR_LOS_B, COLOR_FRESNEL_B, COLOR_OBSTACLE_B,
)
@dataclass
class TerrainArtists:
    """Artistas del panel de terreno."""
    line_terrain_raw: Line2D
    line_terrain_eff: Line2D
    fill_terrain_eff: PolyCollection
    line_los: Line2D
    fill_fresnel: PolyCollection
    line_fresnel_60: Line2D
    line_mast_tx: Line2D
    line_mast_rx: Line2D
    marker_obstacle: Line2D
    text_obstacle: Text
    line_los_b: Line2D
    line_fresnel_60_b: Line2D
    marker_obstacle_a: Line2D
    marker_obstacle_b: Line2D
    text_obstacle_a: Text
    text_obstacle_b: Text
@dataclass
class DiffractionArtists:
    """Artistas del panel de curva Gd(v)."""
    line_gd: Line2D
    line_v_zero: Line2D
    marker_v_critical: Line2D
    text_annotation: Text
    marker_v_critical_b: Line2D
    text_annotation_b: Text
def build_terrain_artists(ax: Axes) -> TerrainArtists:
    """Crea todos los artistas del panel de terreno en ax.
    Los artistas se crean con datos vacíos; se actualizan en
    terrain_panel.update().
    Args:
        ax: Axes del panel de terreno.
    Returns:
        TerrainArtists con todos los artistas inicializados.
    """
    # Perfil crudo (gris claro)
    (line_terrain_raw,) = ax.plot(
        [], [], color=COLOR_TERRAIN_RAW, lw=0.8, label="Terreno crudo"
    )
    # Perfil efectivo (relleno oscuro)
    (line_terrain_eff,) = ax.plot(
        [], [], color=COLOR_TERRAIN_EFF, lw=1.2, label="Terreno efectivo"
    )
    # Relleno bajo el perfil efectivo
    fill_terrain_eff = ax.fill_between(
        [], [], 0, color=COLOR_TERRAIN_EFF, alpha=0.35
    )
    # LOS
    (line_los,) = ax.plot(
        [], [], color=COLOR_LOS_A, lw=1.6, label="LOS"
    )
    # Banda de Fresnel (relleno entre h_sup y h_inf)
    fill_fresnel = ax.fill_between(
        [], [], [], color=COLOR_FRESNEL_A, alpha=0.15, label="Banda Fresnel"
    )
    # Umbral del 60%
    (line_fresnel_60,) = ax.plot(
        [], [], color=COLOR_FRESNEL_60_A, lw=0.8,
        linestyle="--", label="60% Fresnel"
    )
    # Mástiles Tx y Rx
    (line_mast_tx,) = ax.plot(
        [], [], color=COLOR_MAST, lw=2.0, solid_capstyle="round"
    )
    (line_mast_rx,) = ax.plot(
        [], [], color=COLOR_MAST, lw=2.0, solid_capstyle="round"
    )
    # Marcador del obstáculo crítico
    (marker_obstacle,) = ax.plot(
        [], [], color=COLOR_OBSTACLE, marker="^",
        markersize=8, linestyle="none", label="Obstáculo crítico"
    )
    # Texto junto al obstáculo
    text_obstacle = ax.text(
        0, 0, "", color=COLOR_OBSTACLE, fontsize=7.5,
        ha="left", va="bottom", visible=False,
    )
    text_obstacle.set_visible(False)  # referencia heredada, nunca se dibuja
    (line_los_b,) = ax.plot([], [], color=COLOR_LOS_B, lw=1.4, label="LOS B")
    (line_fresnel_60_b,) = ax.plot([], [], color=COLOR_FRESNEL_B, lw=0.8,
                                  ls="--", label="60% Fresnel B")
    (marker_obstacle_a,) = ax.plot([], [], "^", color=COLOR_OBSTACLE,
                                  ms=7, ls="none")
    (marker_obstacle_b,) = ax.plot([], [], "s", color=COLOR_OBSTACLE_B,
                                  ms=6, ls="none")
    text_obstacle_a = ax.text(0, 0, "", color=COLOR_OBSTACLE, fontsize=7,
                              ha="center", va="bottom")
    text_obstacle_b = ax.text(0, 0, "", color=COLOR_OBSTACLE_B, fontsize=7,
                              ha="center", va="bottom")
    ax.set_xlabel("Distancia [m]")
    ax.set_ylabel("Elevación [m]")
    ax.set_title("Perfil del radioenlace")
    ax.legend(
        loc="upper right", fontsize=7,
        facecolor="#161B22", edgecolor="#30363D",
        labelcolor="#C9D1D9",
    )
    return TerrainArtists(
        line_terrain_raw=line_terrain_raw,
        line_terrain_eff=line_terrain_eff,
        fill_terrain_eff=fill_terrain_eff,
        line_los=line_los,
        fill_fresnel=fill_fresnel,
        line_fresnel_60=line_fresnel_60,
        line_mast_tx=line_mast_tx,
        line_mast_rx=line_mast_rx,
        marker_obstacle=marker_obstacle,
        text_obstacle=text_obstacle,
        line_los_b=line_los_b, line_fresnel_60_b=line_fresnel_60_b,
        marker_obstacle_a=marker_obstacle_a, marker_obstacle_b=marker_obstacle_b,
        text_obstacle_a=text_obstacle_a, text_obstacle_b=text_obstacle_b,
    )
def build_diffraction_artists(ax: Axes) -> DiffractionArtists:
    """Crea los artistas del panel de difracción.
    Curva Gd(v) para 500 puntos en [−3, 3]. Los artistas se crean
    con la curva completa (no cambia con el perfil); solo el marcador
    del punto de operación se actualiza.
    Args:
        ax: Axes del panel de difracción.
    Returns:
        DiffractionArtists con todos los artistas inicializados.
    """
    from core.diffraction import diffraction_gain_db
    v_arr = np.linspace(-3.0, 3.0, 500)
    gd_arr = np.array([diffraction_gain_db(float(v)) for v in v_arr])
    (line_gd,) = ax.plot(
        v_arr, gd_arr, color=COLOR_GD_CURVE, lw=1.5, label=r"$G_d(v)$"
    )
    # Línea vertical en v = 0
    line_v_zero = ax.axvline(
        x=0.0, color=COLOR_V_ZERO, lw=0.8, linestyle="--", label="v = 0"
    )
    # Línea horizontal de referencia en 0 dB
    ax.axhline(y=0.0, color="#444444", lw=0.6, linestyle=":")
    # Marcador del punto de operación
    (marker_v_critical,) = ax.plot(
        [], [], color=COLOR_OBSTACLE, marker="o",
        markersize=7, linestyle="none", label="Punto operación", zorder=5,
    )
    # Anotación numérica del punto de operación
    text_annotation = ax.text(
        0, 0, "", color=COLOR_OBSTACLE, fontsize=7.5,
        ha="left", va="bottom", visible=False,
    )
    (marker_v_critical_b,) = ax.plot([], [], color=COLOR_OBSTACLE_B, marker="s",
                                    markersize=7, linestyle="none",
                                    label="Diseño B", zorder=5)
    text_annotation_b = ax.text(0, 0, "", color=COLOR_OBSTACLE_B, fontsize=7.5,
                                ha="left", va="bottom", visible=False)
    ax.set_xlabel("v  [-]")
    ax.set_ylabel(r"$G_d$ [dB]")
    ax.set_title(r"Curva de difracción $G_d(v)$")
    ax.legend(
        loc="lower left", fontsize=7,
        facecolor="#161B22", edgecolor="#30363D",
        labelcolor="#C9D1D9",
    )
    return DiffractionArtists(
        line_gd=line_gd,
        line_v_zero=line_v_zero,
        marker_v_critical=marker_v_critical,
        text_annotation=text_annotation,
        marker_v_critical_b=marker_v_critical_b,
        text_annotation_b=text_annotation_b,
    )
