"""
Callbacks de los widgets interactivos (Etapa 8).
Cada handler recibe la instancia de App y usa dataclasses.replace()
para crear nuevos LinkParams inmutables antes de llamar app._recompute().
No se permite mutación directa de params.
Referencia: ARCH v1.1, §7; IMPL v1.1, §Etapa 8.
"""
from __future__ import annotations
from dataclasses import replace
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ui.app import App
# ---------------------------------------------------------------------------
# Sliders de parámetros físicos
# ---------------------------------------------------------------------------
def on_freq_changed(val: float, app: "App") -> None:
    """Callback del slider de frecuencia.
    Crea un nuevo LinkParams con f_hz = val * 1e9 (valor en GHz)
    y recalcula el perfil.
    Args:
        val: Frecuencia en GHz (valor del slider).
        app: Instancia de App.
    """
    app.params = replace(app.params, f_hz=float(val) * 1e9)
    app.params_b = replace(app.params_b, f_hz=float(val) * 1e9)
    app._recompute()
def on_k_changed(val: float, app: "App") -> None:
    """Callback del slider de K (factor de escala terrestre).
    Actualiza el campo de texto dN/dh (solo lectura) con el gradiente
    equivalente y recalcula el perfil.
    Args:
        val: Valor de K (adimensional).
        app: Instancia de App.
    """
    from core.atmosphere import gradient_from_k
    app.params = replace(app.params, K=float(val))
    app.params_b = replace(app.params_b, K=float(val))
    # Actualizar label informativo de dN/dh
    if app.text_dndh is not None:
        dndh = gradient_from_k(float(val))
        app.text_dndh.set_text(f"{float(val):.2f} | {dndh:.1f} N/km")
    app._recompute()
def on_htx_changed(val: float, app: "App") -> None:
    """Callback del slider de altura de antena Tx.
    Args:
        val: Altura Tx en metros.
        app: Instancia de App.
    """
    app.params = replace(app.params, h_tx_m=float(val))
    app._recompute()
def on_hrx_changed(val: float, app: "App") -> None:
    """Callback del slider de altura de antena Rx.
    Args:
        val: Altura Rx en metros.
        app: Instancia de App.
    """
    app.params = replace(app.params, h_rx_m=float(val))
    app._recompute()

def on_htx_b_changed(val: float, app: "App") -> None:
    app.params_b = replace(app.params_b, h_tx_m=float(val))
    app._recompute()

def on_hrx_b_changed(val: float, app: "App") -> None:
    app.params_b = replace(app.params_b, h_rx_m=float(val))
    app._recompute()
# ---------------------------------------------------------------------------
# Toggle de terreno crudo / efectivo
# ---------------------------------------------------------------------------
def on_toggle_raw_terrain(label: str, app: "App") -> None:
    """Toggle de visibilidad del perfil crudo.
    Solo modifica la visibilidad del artista; no recalcula física.
    Args:
        label: Etiqueta del CheckButton (ignorada; solo el estado importa).
        app:   Instancia de App.
    """
    current = app.terrain_artists.line_terrain_raw.get_visible()
    app.terrain_artists.line_terrain_raw.set_visible(not current)
    app.fig.canvas.draw_idle()

def on_toggle_design_b(label: str, app: "App") -> None:
    app.show_design_b = not app.show_design_b
    app._render(app.profile)

def on_toggle_power_budget(label: str, app: "App") -> None:
    """Activa/desactiva el budget y recalcula ambos diseños en el core."""
    app.show_power_budget = not app.show_power_budget
    app._recompute()
# ---------------------------------------------------------------------------
# Botones de carga de casos de validación
# ---------------------------------------------------------------------------
def on_load_case_v1(event, app: "App") -> None:
    """Botón V-1: carga caso tierra plana y recalcula.
    Args:
        event: Evento de matplotlib (ignorado).
        app:   Instancia de App.
    """
    from validation.cases import case_flat_earth
    terrain, params = case_flat_earth()
    app.terrain = terrain
    app.params = params
    app.params_b = replace(params)
    app._recompute()
    app._sync_sliders_to_params()
def on_load_case_v2(event, app: "App") -> None:
    """Botón V-2: carga caso borde en LOS y recalcula.
    Args:
        event: Evento de matplotlib (ignorado).
        app:   Instancia de App.
    """
    from validation.cases import case_edge_on_los
    terrain, params = case_edge_on_los()
    app.terrain = terrain
    app.params = params
    app.params_b = replace(params)
    app._recompute()
    app._sync_sliders_to_params()
def on_load_case_v3(event, app: "App") -> None:
    """Botón V-3: carga caso Lima y recalcula.
    Args:
        event: Evento de matplotlib (ignorado).
        app:   Instancia de App.
    """
    from validation.cases import case_lima
    terrain, params = case_lima()
    app.terrain = terrain
    app.params = params
    app.params_b = replace(params)
    app._recompute()
    app._sync_sliders_to_params()
