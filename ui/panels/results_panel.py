"""
Panel de resultados: tabla numérica con los valores clave del LinkProfile.
No recalcula física. Solo formatea y muestra los escalares de LinkProfile.
Referencia: ARCH v1.1, §7.
"""
from __future__ import annotations
from matplotlib.axes import Axes
from models.profile import LinkProfile
# Líneas de texto precreadas (lista de Text)
_NUM_LINES = 16
def build_results_panel(ax: Axes) -> list:
    """Crea las líneas de texto del panel de resultados.
    Args:
        ax: Axes del panel de resultados.
    Returns:
        Lista de Text objects (uno por línea de la tabla).
    """
    ax.set_axis_off()
    ax.set_title("Resultados", color="#C9D1D9", fontsize=9, pad=6)
    texts = []
    for i in range(_NUM_LINES):
        t = ax.text(
            0.05,
            1.0 - (i + 1) * (1.0 / (_NUM_LINES + 1)),
            "",
            transform=ax.transAxes,
            fontsize=8,
            color="#C9D1D9",
            va="center",
            ha="left",
            fontfamily="monospace",
        )
        texts.append(t)
    return texts
def update_results_panel(
    texts: list,
    profile: LinkProfile,
) -> None:
    """Actualiza el panel de resultados con los valores del LinkProfile.
    Args:
        texts:   Lista de Text creados por build_results_panel().
        profile: LinkProfile producido por compute_link_profile().
    """
    p = profile.params
    t = profile.terrain
    idx = profile.idx_critical
    c_los = profile.c_los_m[idx]
    c_ffz = profile.c_ffz_m[idx]
    is_clear = (profile.l_d_db == 0.0) or (profile.v_critical <= -0.78)
    status_str = " (Despejado)" if is_clear else ""

    # Construir tabla de resultados
    f_ghz = p.f_hz / 1e9
    d_km = t.d_total_m / 1e3
    rows = [
        ("── Parámetros ──────────────", ""),
        ("Frecuencia",                  f"{f_ghz:.3f} GHz"),
        ("Distancia",                   f"{d_km:.3f} km"),
        ("Factor K",                    f"{p.K:.4f}"),
        ("h Tx",                        f"{p.h_tx_m:.2f} m"),
        ("h Rx",                        f"{p.h_rx_m:.2f} m"),
        ("── Difracción ──────────────", ""),
        ("v crítico",                   f"{profile.v_critical:.4f}"),
        ("C_LOS",                       f"{c_los:+.2f} m"),
        ("C_FFZ",                       f"{c_ffz:+.2f} m"),
        ("Gd(v)",                       f"{profile.g_d_db:.4f} dB"),
        ("Ld(v)",                       f"{profile.l_d_db:.4f} dB{status_str}"),
        ("── Enlace ──────────────────", ""),
        ("Lfs",                         f"{profile.l_fs_db:.2f} dB"),
        ("Prx (sin budget)",            "—" if profile.p_rx_dbm is None
                                        else f"{profile.p_rx_dbm:.2f} dBm"),
        ("Disponibilidad",              "—" if profile.availability_pct is None
                                        else f"{profile.availability_pct:.4f} %"),
    ]
    # Rellenar textos con las filas disponibles
    for i, text_obj in enumerate(texts):
        if i < len(rows):
            label, value = rows[i]
            if value:
                line = f"{label:<28} {value}"
            else:
                line = label  # encabezado de sección
            text_obj.set_text(line)
            # Diferenciar encabezados
            if value == "":
                text_obj.set_color("#58A6FF")
                text_obj.set_fontsize(7.5)
            else:
                text_obj.set_color("#C9D1D9")
                text_obj.set_fontsize(8)
        else:
            text_obj.set_text("")
