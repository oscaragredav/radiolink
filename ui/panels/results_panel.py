"""Tabla comparativa de resultados de los diseños A y B."""
from __future__ import annotations

from matplotlib.axes import Axes
from models.profile import LinkProfile


class ResultCells(list):
    """Lista compatible con Etapa 8 que además conserva la tabla nativa."""
    def __init__(self, table):
        self.table = table
        super().__init__(cell.get_text() for cell in table.get_celld().values())


def build_results_panel(ax: Axes) -> ResultCells:
    ax.set_axis_off()
    ax.set_title("Resultados", color="#C9D1D9", fontsize=9, pad=6)
    labels = ["hTx", "hRx", "v_crit", "C_LOS", "C_FFZ", "Gd", "Ld",
              "Estado", "Lfs", "Lat/Lon", "Prx", "Margen M",
              "Disponibilidad"]
    table = ax.table(cellText=[[label, "—", "—", "—"] for label in labels],
                     colLabels=["Parámetro", "Diseño A", "Diseño B", "Dif."],
                     colWidths=[0.28, 0.24, 0.24, 0.20], cellLoc="right",
                     bbox=[0.01, 0.01, 0.98, 0.96])
    table.auto_set_font_size(False)
    table.set_fontsize(6.5)
    for (row, col), cell in table.get_celld().items():
        cell.set_facecolor("#0D1117")
        cell.set_edgecolor("#0D1117")
        cell.set_linewidth(0)
        cell.get_text().set_color("#C9D1D9")
        cell.get_text().set_ha("left" if col == 0 else "right")
        if row == 0:
            cell.get_text().set_color("#58A6FF")
            cell.get_text().set_weight("bold")
    return ResultCells(table)


def _values(profile: LinkProfile) -> tuple[list[str], list[float | None]]:
    p, t, i = profile.params, profile.terrain, profile.idx_critical
    latlon = "—"
    if not t.is_synthetic and t.lat is not None and t.lon is not None:
        latlon = f"{t.lat[i]:.5f}, {t.lon[i]:.5f}"
    clear = profile.l_d_db == 0.0
    shown = [f"{p.h_tx_m:.2f} m", f"{p.h_rx_m:.2f} m",
             f"{profile.v_critical:.4f}", f"{profile.c_los_m[i]:+.2f} m",
             f"{profile.c_ffz_m[i]:+.2f} m", f"{profile.g_d_db:.4f} dB",
             f"{profile.l_d_db:.4f} dB", "Despejado" if clear else "Obstruido",
             f"{profile.l_fs_db:.2f} dB", latlon,
             "—" if profile.p_rx_dbm is None else f"{profile.p_rx_dbm:.2f} dBm",
             "—" if profile.margin_db is None else f"{profile.margin_db:.2f} dB",
             "—" if profile.availability_pct is None
             else f"{profile.availability_pct:.3f}%"]
    numeric = [p.h_tx_m, p.h_rx_m, profile.v_critical,
               float(profile.c_los_m[i]), float(profile.c_ffz_m[i]),
               profile.g_d_db, profile.l_d_db, None, profile.l_fs_db, None,
               profile.p_rx_dbm, profile.margin_db, profile.availability_pct]
    return shown, numeric


def update_results_panel(cells: ResultCells, profile: LinkProfile,
                         profile_b: LinkProfile | None = None) -> None:
    a, an = _values(profile)
    b, bn = _values(profile_b or profile)
    for row, (av, bv, avn, bvn) in enumerate(zip(a, b, an, bn), start=1):
        cells.table[(row, 1)].get_text().set_text(av)
        cells.table[(row, 2)].get_text().set_text(bv if profile_b else "—")
        diff = "—" if profile_b is None or avn is None else f"{bvn - avn:+.2f}"
        cells.table[(row, 3)].get_text().set_text(diff)

    # Solo el texto de Margen comunica el estado; el fondo permanece neutro.
    margin_row = 12
    for col, current in ((1, profile), (2, profile_b)):
        text = cells.table[(margin_row, col)].get_text()
        text.set_color("#C9D1D9")
        if current is not None and current.margin_db is not None:
            margin = current.margin_db
            text.set_color("#3FB950" if margin >= 10.0 else
                           "#D29922" if margin >= 0.0 else "#F85149")
