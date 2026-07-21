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
    profile_b: LinkProfile | None = None,
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
    # --- Ajuste automático de ejes ---
    y_min = min(terrain.elevation_m.min(), profile.z_eff_m.min())
    h_max_a = max(profile.params.h_tx_m, profile.params.h_rx_m)
    h_max_b = (max(profile_b.params.h_tx_m, profile_b.params.h_rx_m)
               if profile_b is not None else 0.0)
    top_y = float(np.max(profile.z_eff_m)) + max(h_max_a, h_max_b) + 20.0
    ax.set_xlim(0, terrain.d_total_m)
    ax.set_ylim(y_min - 5.0, top_y)

    # --- Obstáculo crítico ---
    idx = profile.idx_critical
    d_obs = d_m[idx]
    z_obs = profile.z_eff_m[idx]
    c_los = profile.c_los_m[idx]
    c_ffz = profile.c_ffz_m[idx]

    # Referencias heredadas invisibles; la UI visible marca la cima real.
    artists.marker_obstacle.set_data([d_obs], [y_min - 3])
    artists.text_obstacle.set_position((d_obs + d_m[-1] * 0.01, y_min - 3))
    
    is_clear = profile.l_d_db == 0.0
    status = " (Despejado)" if is_clear else ""
    artists.text_obstacle.set_text(
        f"Elev: {z_obs:.1f} m\n"
        f"C_LOS: {c_los:+.2f} m | C_FFZ: {c_ffz:+.2f} m\n"
        f"v={profile.v_critical:.3f}\n"
        f"Ld={profile.l_d_db:.2f} dB{status}"
    )
    artists.text_obstacle.set_visible(True)
    artists.text_obstacle.set_visible(False)
    artists.marker_obstacle.set_visible(False)
    artists.marker_obstacle_a.set_data([d_obs], [z_obs])
    artists.text_obstacle_a.set_position((d_obs, z_obs + 3))
    artists.text_obstacle_a.set_text(f"A: z={z_obs:.1f}m")

    if profile_b is not None:
        ib = profile_b.idx_critical
        db, zb = d_m[ib], profile_b.z_eff_m[ib]
        artists.line_los_b.set_data(d_m, profile_b.h_los_m)
        artists.line_fresnel_60_b.set_data(d_m, profile_b.h_60pct_m)
        artists.marker_obstacle_b.set_data([db], [zb])
        artists.text_obstacle_b.set_position((db, zb + 3))
        artists.text_obstacle_b.set_text(f"B: z={zb:.1f}m")
        artists.line_los_b.set_visible(True)
        artists.line_fresnel_60_b.set_visible(True)
        artists.marker_obstacle_b.set_visible(True)
        artists.text_obstacle_b.set_visible(True)
    else:
        for artist in (artists.line_los_b, artists.line_fresnel_60_b,
                       artists.marker_obstacle_b, artists.text_obstacle_b):
            artist.set_visible(False)
