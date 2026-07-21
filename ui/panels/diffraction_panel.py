"""Panel comparativo de la curva de difracción."""
from matplotlib.axes import Axes
from models.profile import LinkProfile
from ui.artists import DiffractionArtists, update_diffraction_curve


def update_diffraction_panel(ax: Axes, artists: DiffractionArtists,
                             profile: LinkProfile,
                             profile_b: LinkProfile | None = None) -> None:
    v_c, gd_c = profile.v_critical, profile.g_d_db
    v_cb = profile_b.v_critical if profile_b else v_c
    gd_cb = profile_b.g_d_db if profile_b else gd_c
    artists.marker_v_critical.set_data([v_c], [gd_c])
    artists.text_annotation.set_position((v_c + .05, gd_c + .5))
    artists.text_annotation.set_text(f"A: v={v_c:.3f}, Gd={gd_c:.2f} dB")
    artists.text_annotation.set_visible(True)
    artists.marker_v_critical_b.set_data([v_cb], [gd_cb])
    artists.marker_v_critical_b.set_visible(profile_b is not None)
    artists.text_annotation_b.set_position((v_cb + .05, gd_cb - .7))
    artists.text_annotation_b.set_text(f"B: v={v_cb:.3f}, Gd={gd_cb:.2f} dB")
    artists.text_annotation_b.set_visible(profile_b is not None)
    x_min = min(-3.0, v_c - 0.4, v_cb - 0.4)
    x_max = max(3.0, v_c + 0.4, v_cb + 0.4)
    update_diffraction_curve(artists, x_min, x_max)
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(min(-24.0, gd_c - 4.0, gd_cb - 4.0), 6.0)
