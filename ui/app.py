"""
Controlador principal de la aplicación de visualización de radioenlace.

Etapa 8: versión interactiva con sliders (frecuencia, K, hTx, hRx),
toggle de terreno crudo/efectivo y botones de carga de casos V-1/V-2/V-3.

Referencia: ARCH v1.1, §7; IMPL v1.1, §Etapa 8.

Reglas:
  - La UI no recalcula física directamente; delega en core.engine.
  - Los callbacks usan dataclasses.replace(); nunca mutan params directamente.
  - El toggle de terreno solo modifica visibilidad de artistas; no recalcula.
"""

from __future__ import annotations

from typing import Optional

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.widgets import Slider, Button, CheckButtons

from core.atmosphere import gradient_from_k
from core.engine import compute_link_profile
from models.params import LinkParams, PowerBudgetParams
from models.terrain import TerrainData
from models.profile import LinkProfile

from ui.layout import (
    build_figure,
    build_widget_axes,
    COLOR_SLIDER_COLOR,
    COLOR_WIDGET_TEXT,
    COLOR_BTN_FACE,
)
from ui.artists import (
    build_terrain_artists,
    build_diffraction_artists,
    TerrainArtists,
    DiffractionArtists,
)
from ui.panels.terrain_panel import draw_terrain_panel
from ui.panels.diffraction_panel import update_diffraction_panel
from ui.panels.results_panel import build_results_panel, update_results_panel
from ui.callbacks import (
    on_freq_changed,
    on_k_changed,
    on_htx_changed,
    on_hrx_changed,
    on_toggle_raw_terrain,
    on_load_case_v1,
    on_load_case_v2,
    on_load_case_v3,
    on_htx_b_changed, on_hrx_b_changed, on_toggle_design_b,
    on_toggle_power_budget,
)


class App:
    """Controlador de la figura matplotlib con widgets interactivos.

    Atributos públicos (modificados por callbacks vía dataclasses.replace):
        terrain:   Datos del perfil de terreno actual.
        params:    Parámetros del enlace actuales (LinkParams inmutable).
        pb_params: Parámetros de power budget (opcional).
        profile:   Último LinkProfile calculado.
        text_dndh: Text que muestra dN/dh actualizado por el slider de K.
    
    Args:
        terrain:   Datos del perfil de terreno.
        params:    Parámetros del enlace (opcional; usa defaults si None).
        pb_params: Parámetros de power budget (opcional).
    """


    def __init__(
        self,
        terrain: TerrainData,
        params: Optional[LinkParams] = None,
        pb_params: Optional[PowerBudgetParams] = None,
    ) -> None:
          # Parámetros por defecto
        if params is None:
            params = LinkParams(
                f_hz=7e9,
                h_tx_m=10.0,
                h_rx_m=10.0,
                K=4 / 3,
            )

        self.terrain = terrain
        self.params = params
        self.params_b = params
        self.show_design_b = True
        # Defaults compactos y configurables desde el constructor.
        self.pb_params = pb_params or PowerBudgetParams(
            p_tx_dbm=30.0, g_tx_dbi=25.0, g_rx_dbi=25.0,
            l_cable_tx_db=1.0, l_cable_rx_db=1.0,
            sensitivity_dbm=-80.0, a_climate=0.5, b_terrain=1.0,
        )
        self.show_power_budget = pb_params is not None
        self.text_dndh: Optional[object] = None  # Text de dN/dh (etapa 8)

        # ── Figura y paneles de datos ──────────────────────────────────
        self.fig, self.ax_terrain, self.ax_diffraction, self.ax_results = (
            build_figure()
        )
        # ── Artistas (creados una sola vez) ───────────────────────────
        self.terrain_artists: TerrainArtists = build_terrain_artists(
            self.ax_terrain
        )
        self.diffraction_artists: DiffractionArtists = build_diffraction_artists(
            self.ax_diffraction
        )
        self.result_texts = build_results_panel(self.ax_results)
        
        # ── Widgets interactivos ──────────────────────────────────────
        self._widget_axes = build_widget_axes(self.fig)
        self._build_widgets()
        
        # ── Calcular perfil inicial y renderizar ──────────────────────
        self.profile: LinkProfile = compute_link_profile(
            self.params, self.terrain, self._active_pb_params()
        )
        self.profile_b: LinkProfile = compute_link_profile(
            self.params_b, self.terrain, self._active_pb_params()
        )
        self._render(self.profile)
        self._sync_sliders_to_params()
    
    #  ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------
    
    def show(self) -> None:
        """Muestra la figura (bloquea hasta que se cierre la ventana)."""
        plt.show()
    
    def save(self, path: str, dpi: int = 140) -> None:
        """Guarda la figura como imagen.
        Args:
            path: Ruta del archivo (png, pdf, svg…).
            dpi:  Resolución de exportación.
        """
        self.fig.savefig(
            path, dpi=dpi, bbox_inches="tight",
            facecolor=self.fig.get_facecolor(),
        )

    # ------------------------------------------------------------------
    # Métodos internos
    # ------------------------------------------------------------------
    
    def _build_widgets(self) -> None:
        """Instancia y conecta todos los widgets."""
        wa = self._widget_axes
        # ── Sliders ────────────────────────────────────────────────────
        self._sl_freq = Slider(
            ax=wa.ax_slider_freq,
            label="Frec [GHz]",
            valmin=0.1,
            valmax=30.0,
            valinit=self.params.f_hz / 1e9,
            color=COLOR_SLIDER_COLOR,
        )
        self._sl_k = Slider(
            ax=wa.ax_slider_k,
            label="K [-]",
            valmin=0.5,
            valmax=3.0,
            valinit=self.params.K,
            color=COLOR_SLIDER_COLOR,
        )
        self._sl_htx = Slider(
            ax=wa.ax_slider_htx,
            label="h Tx [m]",
            valmin=1.0,
            valmax=100.0,
            valinit=self.params.h_tx_m,
            color=COLOR_SLIDER_COLOR,
        )
        self._sl_hrx = Slider(
            ax=wa.ax_slider_hrx,
            label="h Rx [m]",
            valmin=1.0,
            valmax=100.0,
            valinit=self.params.h_rx_m,
            color=COLOR_SLIDER_COLOR,
        )
        self._sl_htx_b = Slider(
            ax=wa.ax_slider_htx_b, label="h Tx [m]", valmin=1.0,
            valmax=100.0, valinit=self.params_b.h_tx_m,
            color=COLOR_SLIDER_COLOR,
        )
        self._sl_hrx_b = Slider(
            ax=wa.ax_slider_hrx_b, label="h Rx [m]", valmin=1.0,
            valmax=100.0, valinit=self.params_b.h_rx_m,
            color=COLOR_SLIDER_COLOR,
        )
        # Estilo de los sliders
        for sl in (self._sl_freq, self._sl_k, self._sl_htx, self._sl_hrx,
                   self._sl_htx_b, self._sl_hrx_b):
            sl.label.set_color(COLOR_WIDGET_TEXT)
            sl.valtext.set_color(COLOR_WIDGET_TEXT)
        # ── Texto de dN/dh (actualizado por slider K) ─────────────────
        dndh_init = gradient_from_k(self.params.K)
        self.text_dndh = self._sl_k.valtext
        self.text_dndh.set_text(f"{self.params.K:.2f} | {dndh_init:.1f} N/km")
        # ── Botones de casos ───────────────────────────────────────────
        self._btn_v1 = Button(
            ax=wa.ax_btn_v1, label="V-1",
            color=COLOR_BTN_FACE, hovercolor="#2EA043",
        )
        self._btn_v2 = Button(
            ax=wa.ax_btn_v2, label="V-2",
            color=COLOR_BTN_FACE, hovercolor="#2EA043",
        )
        self._btn_v3 = Button(
            ax=wa.ax_btn_v3, label="Lima",
            color=COLOR_BTN_FACE, hovercolor="#2EA043",
        )
        for btn in (self._btn_v1, self._btn_v2, self._btn_v3):
            btn.label.set_color(COLOR_WIDGET_TEXT)
            btn.label.set_fontsize(8)
        # ── Toggle terreno crudo ───────────────────────────────────────
        self._chk_raw = CheckButtons(
            ax=wa.ax_toggle_raw,
            labels=["Terreno crudo"],
            actives=[True],
        )
        self._chk_design_b = CheckButtons(
            ax=wa.ax_toggle_design_b, labels=["Diseño B"], actives=[True]
        )
        self._chk_power_budget = CheckButtons(
            ax=wa.ax_toggle_power_budget, labels=["Power Budget"],
            actives=[self.show_power_budget]
        )
        try:
            # matplotlib >= 3.9 usa set_check_props (solo si acepta facecolor)
            self._chk_raw.set_check_props(facecolor=COLOR_SLIDER_COLOR)
        except (AttributeError, TypeError):
            pass
        # ── Conexión de callbacks ──────────────────────────────────────
        self._sl_freq.on_changed(lambda v: on_freq_changed(v, self))
        self._sl_k.on_changed(lambda v: on_k_changed(v, self))
        self._sl_htx.on_changed(lambda v: on_htx_changed(v, self))
        self._sl_hrx.on_changed(lambda v: on_hrx_changed(v, self))
        self._sl_htx_b.on_changed(lambda v: on_htx_b_changed(v, self))
        self._sl_hrx_b.on_changed(lambda v: on_hrx_b_changed(v, self))
        self._btn_v1.on_clicked(lambda e: on_load_case_v1(e, self))
        self._btn_v2.on_clicked(lambda e: on_load_case_v2(e, self))
        self._btn_v3.on_clicked(lambda e: on_load_case_v3(e, self))
        self._chk_raw.on_clicked(lambda lbl: on_toggle_raw_terrain(lbl, self))
        self._chk_design_b.on_clicked(lambda lbl: on_toggle_design_b(lbl, self))
        self._chk_power_budget.on_clicked(
            lambda lbl: on_toggle_power_budget(lbl, self)
        )
        # Añadir etiquetas descriptivas sobre los sliders y botones
        self._add_widget_labels()
    def _add_widget_labels(self) -> None:
        """Añade textos decorativos a la zona de widgets."""
        wa = self._widget_axes
        wa.ax_slider_freq.set_title("Diseño A", color="#58A6FF", fontsize=8,
                                    fontweight="bold", loc="left", pad=5)
        wa.ax_slider_htx_b.set_title("Diseño B", color="#58A6FF", fontsize=8,
                                     fontweight="bold", loc="left", pad=5)
        wa.ax_btn_v1.set_title("Casos", color="#58A6FF", fontsize=8,
                               fontweight="bold", loc="left", pad=5)

    def _render(self, profile: LinkProfile) -> None:
        """Actualiza todos los paneles con el perfil dado."""
        profile_b = self.profile_b if self.show_design_b else None
        draw_terrain_panel(self.ax_terrain, self.terrain_artists, profile, profile_b)
        update_diffraction_panel(
            self.ax_diffraction, self.diffraction_artists, profile, profile_b
        )
        update_results_panel(self.result_texts, profile, profile_b)
        self.fig.canvas.draw_idle()
    
    def _recompute(self) -> None:
        """Recalcula el perfil con los parámetros actuales y actualiza la UI.

        Llamado por todos los callbacks de widgets.
        """
        self.profile = compute_link_profile(
            self.params, self.terrain, self._active_pb_params()
        )
        self.profile_b = compute_link_profile(
            self.params_b, self.terrain, self._active_pb_params()
        )
        self._render(self.profile)

    def _active_pb_params(self) -> Optional[PowerBudgetParams]:
        """Budget configurado cuando el checkbox está activo."""
        return self.pb_params if self.show_power_budget else None

    def _sync_sliders_to_params(self) -> None:
        """Sincroniza los sliders con los valores actuales de self.params.
        Útil después de cargar un caso de validación: los sliders se
        mueven a los nuevos valores sin disparar callbacks.
        """
        self._sl_freq.set_val(self.params.f_hz / 1e9)
        self._sl_k.set_val(self.params.K)
        self._sl_htx.set_val(self.params.h_tx_m)
        self._sl_hrx.set_val(self.params.h_rx_m)
        self._sl_htx_b.set_val(self.params_b.h_tx_m)
        self._sl_hrx_b.set_val(self.params_b.h_rx_m)
        if self.text_dndh is not None:
            dndh = gradient_from_k(self.params.K)
            self.text_dndh.set_text(f"{self.params.K:.2f} | {dndh:.1f} N/km")

def _btn_label_x(wa) -> float:
    """Posición X del label de botones."""
    try:
        return wa.ax_btn_v1.get_position().x0
    except Exception:
        return 0.67
