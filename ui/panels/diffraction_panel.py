"""
Panel de difracción: curva Gd(v) y punto de operación.

La curva Gd(v) se dibuja una sola vez en build_diffraction_artists().
Este módulo solo actualiza el marcador del punto de operación.

No importa ninguna función física de core/ salvo la ya usada por artists.py
para construir la curva estática.

Referencia: ARCH v1.1, §7.
"""

from __future__ import annotations

from matplotlib.axes import Axes

from models.profile import LinkProfile
from ui.artists import DiffractionArtists


def update_diffraction_panel(
    ax: Axes,
    artists: DiffractionArtists,
    profile: LinkProfile,
) -> None:
    """Actualiza el marcador del punto de operación en el panel de difracción.

    La curva Gd(v) permanece fija. Solo se mueve el marcador al punto
    (v_critical, g_d_db) del LinkProfile actual.

    Args:
        ax:       Axes del panel de difracción (solo para ajuste de límites).
        artists:  DiffractionArtists creados por build_diffraction_artists().
        profile:  LinkProfile producido por compute_link_profile().
    """
    v_c = profile.v_critical
    gd_c = profile.g_d_db

    # Mover marcador
    artists.marker_v_critical.set_data([v_c], [gd_c])

    # Actualizar anotación
    artists.text_annotation.set_position((v_c + 0.05, gd_c + 0.5))
    artists.text_annotation.set_text(
        f"v={v_c:.3f}\n$G_d$={gd_c:.2f} dB"
    )
    artists.text_annotation.set_visible(True)

    # Ajuste fino de ejes para que el marcador sea siempre visible
    # El rango base es [−3, 3]; si v_c está fuera, ampliar
    x_min = min(-3.0, v_c - 0.3)
    x_max = max(3.0, v_c + 0.3)
    ax.set_xlim(x_min, x_max)
