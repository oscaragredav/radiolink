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
    on_load_api,
    on_ptx_changed, on_gtx_changed, on_grx_changed, on_sensitivity_changed,
    on_toggle_mobile_obstacle, on_mobile_total_changed,
    on_mobile_position_changed, on_mobile_height_changed,
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
            p_tx_dbm=20.0, g_tx_dbi=24.0, g_rx_dbi=24.0,
            l_cable_tx_db=0.0, l_cable_rx_db=0.0,
            sensitivity_dbm=-85.0, a_climate=0.5, b_terrain=1.0,
        )
        self.show_power_budget = pb_params is not None
        self.mobile_mode = False
        self._updating_mobile = False
        self._terrain_before_mobile = None
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
        self._sl_ptx = Slider(
            ax=wa.ax_slider_ptx, label="Ptx [dBm]", valmin=0.0, valmax=30.0,
            valinit=self.pb_params.p_tx_dbm, color=COLOR_SLIDER_COLOR,
        )
        self._sl_gtx = Slider(
            ax=wa.ax_slider_gtx, label="Gtx [dBi]", valmin=0.0, valmax=40.0,
            valinit=self.pb_params.g_tx_dbi, color=COLOR_SLIDER_COLOR,
        )
        self._sl_grx = Slider(
            ax=wa.ax_slider_grx, label="Grx [dBi]", valmin=0.0, valmax=40.0,
            valinit=self.pb_params.g_rx_dbi, color=COLOR_SLIDER_COLOR,
        )
        self._sl_sensitivity = Slider(
            ax=wa.ax_slider_sensitivity, label="Sens Rx", valmin=-110.0,
            valmax=-60.0, valinit=self.pb_params.sensitivity_dbm,
            color=COLOR_SLIDER_COLOR,
        )
        self._sl_d_total = Slider(
            ax=wa.ax_slider_d_total, label="d total [km]", valmin=1.0,
            valmax=50.0, valinit=10.0, color=COLOR_SLIDER_COLOR,
        )
        self._sl_d_obs = Slider(
            ax=wa.ax_slider_d_obs, label="d obs [km]", valmin=0.1,
            valmax=9.9, valinit=5.0, color=COLOR_SLIDER_COLOR,
        )
        self._sl_z_obs = Slider(
            ax=wa.ax_slider_z_obs, label="z obs [m]", valmin=0.0,
            valmax=300.0, valinit=0.0, color=COLOR_SLIDER_COLOR,
        )
        # Estilo de los sliders
        for sl in (self._sl_freq, self._sl_k, self._sl_htx, self._sl_hrx,
                   self._sl_htx_b, self._sl_hrx_b, self._sl_ptx,
                   self._sl_gtx, self._sl_grx, self._sl_sensitivity):
            sl.label.set_color(COLOR_WIDGET_TEXT)
            sl.valtext.set_color(COLOR_WIDGET_TEXT)
        for sl in (self._sl_d_total, self._sl_d_obs, self._sl_z_obs):
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
        self._btn_api = Button(
            ax=wa.ax_btn_api, label="Cargar API",
            color=COLOR_BTN_FACE, hovercolor="#434C5E",
        )
        for btn in (self._btn_v1, self._btn_v2, self._btn_v3, self._btn_api):
            btn.label.set_color(COLOR_WIDGET_TEXT)
            btn.label.set_fontsize(8)
        # ── Toggle terreno crudo ───────────────────────────────────────
        self._chk_raw = CheckButtons(
            ax=wa.ax_toggle_raw,
            labels=["Terreno s/K"],
            actives=[True],
        )
        self._chk_design_b = CheckButtons(
            ax=wa.ax_toggle_design_b, labels=["Diseño B"], actives=[True]
        )
        self._chk_power_budget = CheckButtons(
            ax=wa.ax_toggle_power_budget, labels=["Budget Px"],
            actives=[self.show_power_budget]
        )
        self._chk_mobile = CheckButtons(
            ax=wa.ax_toggle_mobile, labels=["Obst. Móvil"],
            actives=[self.mobile_mode]
        )
        for checks in (self._chk_raw, self._chk_design_b,
                       self._chk_power_budget, self._chk_mobile):
            for label in checks.labels:
                label.set_color(COLOR_WIDGET_TEXT)
                label.set_fontsize(8)
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
        self._sl_ptx.on_changed(lambda v: on_ptx_changed(v, self))
        self._sl_gtx.on_changed(lambda v: on_gtx_changed(v, self))
        self._sl_grx.on_changed(lambda v: on_grx_changed(v, self))
        self._sl_sensitivity.on_changed(
            lambda v: on_sensitivity_changed(v, self)
        )
        self._sl_d_total.on_changed(lambda v: on_mobile_total_changed(v, self))
        self._sl_d_obs.on_changed(
            lambda v: on_mobile_position_changed(v, self)
        )
        self._sl_z_obs.on_changed(lambda v: on_mobile_height_changed(v, self))
        self._btn_v1.on_clicked(lambda e: on_load_case_v1(e, self))
        self._btn_v2.on_clicked(lambda e: on_load_case_v2(e, self))
        self._btn_v3.on_clicked(lambda e: on_load_case_v3(e, self))
        self._btn_api.on_clicked(lambda e: on_load_api(e, self))
        self._chk_raw.on_clicked(lambda lbl: on_toggle_raw_terrain(lbl, self))
        self._chk_design_b.on_clicked(lambda lbl: on_toggle_design_b(lbl, self))
        self._chk_power_budget.on_clicked(
            lambda lbl: on_toggle_power_budget(lbl, self)
        )
        self._chk_mobile.on_clicked(
            lambda lbl: on_toggle_mobile_obstacle(lbl, self)
        )
        self._refresh_widget_modes()
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

    def _set_budget_controls_visible(self, visible: bool) -> None:
        """Alterna el modo compacto de edición del presupuesto."""
        self._refresh_widget_modes()

    def _refresh_widget_modes(self) -> None:
        """Distribuye cada grupo sin acoplar los tres estados opcionales."""
        wa = self._widget_axes
        budget_controls = (
            (wa.ax_slider_ptx, self._sl_ptx),
            (wa.ax_slider_gtx, self._sl_gtx),
            (wa.ax_slider_grx, self._sl_grx),
            (wa.ax_slider_sensitivity, self._sl_sensitivity),
        )
        for ax, widget in budget_controls:
            ax.set_visible(self.show_power_budget)
            widget.active = self.show_power_budget

        design_b_controls = (
            (wa.ax_slider_htx_b, self._sl_htx_b),
            (wa.ax_slider_hrx_b, self._sl_hrx_b),
        )
        for ax, widget in design_b_controls:
            ax.set_visible(self.show_design_b)
            widget.active = self.show_design_b

        mobile_controls = (
            (wa.ax_slider_d_total, self._sl_d_total),
            (wa.ax_slider_d_obs, self._sl_d_obs),
            (wa.ax_slider_z_obs, self._sl_z_obs),
        )
        for ax, widget in mobile_controls:
            ax.set_visible(self.mobile_mode)
            widget.active = self.mobile_mode

        # Móvil usa la parte alta del centro si B está apagado, y la parte
        # inferior si ambos están encendidos.
        mobile_ys = ((0.099, 0.062, 0.025) if self.show_design_b
                     else (0.185, 0.142, 0.099))
        for ax, y in zip((wa.ax_slider_d_total, wa.ax_slider_d_obs,
                          wa.ax_slider_z_obs), mobile_ys):
            ax.set_position([0.48, y, 0.11, 0.018])

        # Presets y opciones nunca desaparecen; solo los sliders condicionados.
        always_on = (
            (wa.ax_btn_v1, self._btn_v1), (wa.ax_btn_v2, self._btn_v2),
            (wa.ax_btn_v3, self._btn_v3), (wa.ax_btn_api, self._btn_api),
            (wa.ax_toggle_raw, self._chk_raw),
            (wa.ax_toggle_design_b, self._chk_design_b),
            (wa.ax_toggle_power_budget, self._chk_power_budget),
            (wa.ax_toggle_mobile, self._chk_mobile),
        )
        for ax, widget in always_on:
            ax.set_visible(True)
            widget.active = True
        self.fig.canvas.draw_idle()

    def _toggle_mobile_obstacle_mode(self) -> None:
        """Entra o sale del preset sintético conservando el perfil previo."""
        from dataclasses import replace

        if self.mobile_mode:
            self.mobile_mode = False
            if self._terrain_before_mobile is not None:
                self.terrain, self.params, self.params_b = self._terrain_before_mobile
            self._terrain_before_mobile = None
            self._refresh_widget_modes()
            self._recompute()
            return

        self._terrain_before_mobile = (self.terrain, self.params, self.params_b)
        self.mobile_mode = True
        # El preset móvil siempre comienza mostrando el terreno sin K.
        old_eventson = self._chk_raw.eventson
        self._chk_raw.eventson = False
        try:
            self._chk_raw.set_active(0, True)
        finally:
            self._chk_raw.eventson = old_eventson
        self.terrain_artists.line_terrain_raw.set_visible(True)
        # Alturas del preset plano despejado: con z_obs=0 el core entrega Ld=0.
        self.params = replace(self.params, h_tx_m=10.0, h_rx_m=10.0, K=1e12)
        self.params_b = replace(self.params_b, h_tx_m=10.0, h_rx_m=10.0, K=1e12)
        self._refresh_widget_modes()
        self._update_mobile_terrain(d_total_km=10.0, d_obs_km=5.0,
                                    z_obs_m=0.0)

    def _update_mobile_terrain(self, d_total_km: float | None = None,
                               d_obs_km: float | None = None,
                               z_obs_m: float | None = None) -> None:
        """Regenera terreno y perfil físico en cada movimiento del slider."""
        if not self.mobile_mode or self._updating_mobile:
            return
        from models.terrain import synthetic_obstacle_terrain

        self._updating_mobile = True
        try:
            total = float(self._sl_d_total.val if d_total_km is None
                          else d_total_km)
            max_obs = total - 0.1
            position = float(self._sl_d_obs.val if d_obs_km is None
                             else d_obs_km)
            position = min(max(0.1, position), max_obs)
            height = float(self._sl_z_obs.val if z_obs_m is None else z_obs_m)
            self._sl_d_obs.valmax = max_obs
            self._sl_d_obs.ax.set_xlim(self._sl_d_obs.valmin, max_obs)
            for slider, value in ((self._sl_d_total, total),
                                  (self._sl_d_obs, position),
                                  (self._sl_z_obs, height)):
                old_eventson = slider.eventson
                slider.eventson = False
                slider.set_val(value)
                slider.eventson = old_eventson
            if height == 0.0:
                # Mantiene el caso plano en la zona Gd>=0 para todo 1..50 km.
                from config.constants import C_LIGHT
                from dataclasses import replace
                clearance_h = 1.2 * (C_LIGHT / self.params.f_hz
                                     * (total * 1_000.0) / 8.0) ** 0.5
                self.params = replace(self.params, h_tx_m=clearance_h,
                                      h_rx_m=clearance_h, K=1e12)
                self.params_b = replace(self.params_b, h_tx_m=clearance_h,
                                        h_rx_m=clearance_h, K=1e12)
            self.terrain = synthetic_obstacle_terrain(total, position, height)
            self._recompute()
        finally:
            self._updating_mobile = False

    def load_api_profile(self, tx_lat: float, tx_lon: float,
                         rx_lat: float, rx_lon: float) -> bool:
        """Descarga y aplica un perfil; conserva el actual ante cualquier error."""
        from data.api import TerrainAPIError, fetch_terrain_profile

        old_title = self.ax_terrain.get_title()
        self.ax_terrain.set_title("Descargando perfil topográfico...",
                                  color="#D29922")
        self.fig.canvas.draw_idle()
        try:
            self.fig.canvas.flush_events()
        except NotImplementedError:
            pass
        try:
            terrain = fetch_terrain_profile(tx_lat, tx_lon, rx_lat, rx_lon)
        except (TerrainAPIError, Exception):
            self.ax_terrain.set_title(old_title, color="#C9D1D9")
            self.ax_results.set_title("Error: No se pudo conectar a la API",
                                      color="#F85149", fontsize=9, pad=6)
            self.fig.canvas.draw_idle()
            return False

        self.terrain = terrain
        self.ax_terrain.set_title(old_title, color="#C9D1D9")
        self.ax_results.set_title("Resultados", color="#C9D1D9", fontsize=9, pad=6)
        self._recompute()
        return True

    def open_api_dialog(self) -> None:
        """Solicita Tx/Rx en una ventana compacta, fuera de la figura."""
        try:
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
        except Exception:
            self.ax_results.set_title("Error: No se pudo abrir el diálogo API",
                                      color="#F85149", fontsize=9, pad=6)
            self.fig.canvas.draw_idle()
            return

        root.title("Cargar perfil topográfico")
        root.resizable(False, False)
        defaults = (-12.0464, -77.0428, -12.1211, -77.0297)
        labels = ("Tx Lat", "Tx Lon", "Rx Lat", "Rx Lon")
        entries = []
        for row, (label, value) in enumerate(zip(labels, defaults)):
            tk.Label(root, text=label).grid(row=row, column=0, padx=8, pady=3,
                                            sticky="e")
            entry = tk.Entry(root, width=15)
            entry.insert(0, str(value))
            entry.grid(row=row, column=1, padx=8, pady=3)
            entries.append(entry)

        def submit() -> None:
            try:
                coords = [float(entry.get()) for entry in entries]
            except ValueError:
                messagebox.showerror("Coordenadas", "Ingrese cuatro números válidos")
                return
            root.destroy()
            self.load_api_profile(*coords)

        tk.Button(root, text="Descargar", command=submit).grid(
            row=4, column=0, columnspan=2, pady=8)
        root.mainloop()

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
