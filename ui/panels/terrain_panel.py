"""
Panel de terreno: perfil, LOS, bandas de Fresnel y marcador de obstáculo.

Todos los datos provienen exclusivamente de LinkProfile.
No importa ninguna función física de core/.

Referencia: ARCH v1.1, §7.
"""

from __future__ import annotations

import numpy as np
from matplotlib.axes import Axes

from models.profile import LinkProfile
from ui.artists import TerrainArtists


def draw_terrain_panel(
    ax: Axes,
    artists: TerrainArtists,
    profile: LinkProfile,
) -> None:
    """Dibuja el perfil completo de radioenlace en ax.

    Actualiza los artistas existentes con set_data / set_xy para
    evitar ax.clear(). No recalcula ninguna física.

    Elementos representados:
        - Terreno crudo (elevation_m original).
        - Terreno efectivo (z_eff_m, con relleno).
        - LOS (h_los_m).
        - Banda de Fresnel (h_sup_m / h_inf_m).
        - Umbral del 60% (h_60pct_m).
        - Mástiles Tx y Rx.
        - Marcador del obstáculo crítico.

    Args:
        ax:       Axes del panel de terreno.
        artists:  TerrainArtists creados por build_terrain_artists().
        profile:  LinkProfile producido por compute_link_profile().
    """
    terrain = profile.terrain
    d_m = terrain.d1_m  # distancia desde Tx [m]

    # --- Terreno crudo ---
    artists.line_terrain_raw.set_data(d_m, terrain.elevation_m)

    # --- Terreno efectivo ---
    artists.line_terrain_eff.set_data(d_m, profile.z_eff_m)

    # Relleno bajo el perfil efectivo: reconstruir PolyCollection
    artists.fill_terrain_eff.remove()
    from ui.layout import COLOR_TERRAIN_EFF
    new_fill = ax.fill_between(
        d_m, profile.z_eff_m, terrain.elevation_m.min() - 5,
        color=COLOR_TERRAIN_EFF, alpha=0.35,
    )
    # Reemplazar la referencia en el dataclass (es mutable solo aquí,
    # en el proceso de actualización del artista compuesto)
    artists.__dict__["fill_terrain_eff"] = new_fill

    # --- LOS ---
    artists.line_los.set_data(d_m, profile.h_los_m)

    # --- Banda de Fresnel ---
    artists.fill_fresnel.remove()
    from ui.layout import COLOR_FRESNEL_A
    new_fresnel = ax.fill_between(
        d_m, profile.h_sup_m, profile.h_inf_m,
        color=COLOR_FRESNEL_A, alpha=0.15,
    )
    artists.__dict__["fill_fresnel"] = new_fresnel

    # --- Umbral del 60% ---
    artists.line_fresnel_60.set_data(d_m, profile.h_60pct_m)

    # --- Mástiles ---
    z_tx = terrain.elevation_m[0]
    z_rx = terrain.elevation_m[-1]
    H_tx = z_tx + profile.params.h_tx_m
    H_rx = z_rx + profile.params.h_rx_m
    d_tx = d_m[0]
    d_rx = d_m[-1]

    artists.line_mast_tx.set_data([d_tx, d_tx], [z_tx, H_tx])
    artists.line_mast_rx.set_data([d_rx, d_rx], [z_rx, H_rx])

    # --- Obstáculo crítico ---
    idx = profile.idx_critical
    d_obs = d_m[idx]
    z_obs = profile.z_eff_m[idx]
    artists.marker_obstacle.set_data([d_obs], [z_obs])

    artists.text_obstacle.set_position((d_obs + d_m[-1] * 0.01, z_obs + 2))
    artists.text_obstacle.set_text(
        f"v={profile.v_critical:.3f}\nLd={profile.l_d_db:.2f} dB"
    )
    artists.text_obstacle.set_visible(True)

    # --- Ajuste automático de ejes ---
    y_min = min(terrain.elevation_m.min(), profile.z_eff_m.min()) - 10
    y_max = max(
        profile.h_sup_m.max(),
        profile.h_los_m.max(),
        H_tx, H_rx,
    ) + 20
    ax.set_xlim(d_m[0], d_m[-1])
    ax.set_ylim(y_min, y_max)
