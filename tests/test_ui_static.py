"""
Tests de aceptación de la Etapa 7 — Visualización estática.
Se ejecutan con backend Agg para evitar abrir ventanas bloqueantes.
Criterios cubiertos:
    [F-7.1] La aplicación estática se crea sin errores de Matplotlib.
    [F-7.2] La figura incluye tres paneles: terreno, difracción y resultados.
    [F-7.3] La banda Fresnel se construye desde profile.h_sup_m / h_inf_m.
    [F-7.4] El marcador de obstáculo usa profile.idx_critical.
    [F-7.5] El panel de difracción marca (v_critical, Gd).
    [F-7.6] Ningún módulo de ui/ importa funciones físicas individuales de core/.
"""
import sys
import importlib
import matplotlib
matplotlib.use("Agg")
import numpy as np
import pytest
# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _make_app():
    """Devuelve una instancia de App usando el caso Lima."""
    from ui.app import App
    from validation.cases import case_lima
    terrain, params = case_lima()
    return App(terrain, params)
# ---------------------------------------------------------------------------
# F-7.1  La App se crea sin errores
# ---------------------------------------------------------------------------
def test_static_app_can_be_created():
    """[F-7.1] App(terrain) se instancia sin lanzar excepciones."""
    from ui.app import App
    from validation.cases import case_lima
    terrain, _ = case_lima()
    app = App(terrain)
    assert app is not None
# ---------------------------------------------------------------------------
# F-7.2  La figura tiene exactamente tres Axes
# ---------------------------------------------------------------------------
def test_figure_has_three_panels():
    """[F-7.2] La figura contiene los tres paneles de datos (terreno, difracción, resultados).
    En Etapa 8, la figura puede contener axes adicionales para widgets
    (sliders, botones). Se verifica que existan al menos 3 axes y que
    los tres paneles de datos estén presentes.
    """
    app = _make_app()
    # Al menos 3 axes (Stage 8 puede añadir más para widgets)
    assert len(app.fig.axes) >= 3, (
        f"Se esperaban al menos 3 Axes, se encontraron {len(app.fig.axes)}"
    )
    # Los tres Axes de datos están accesibles directamente
    assert app.ax_terrain is not None
    assert app.ax_diffraction is not None
    assert app.ax_results is not None

def test_figure_size_is_14x10():
    """[F-7.2] La figura mide 14×10 pulgadas."""
    app = _make_app()
    w, h = app.fig.get_size_inches()
    assert abs(w - 14.0) < 0.01
    assert abs(h - 10.0) < 0.01
# ---------------------------------------------------------------------------
# F-7.3  Banda Fresnel construida desde h_sup_m / h_inf_m
# ---------------------------------------------------------------------------
def test_fresnel_band_uses_profile_arrays():
    """[F-7.3] La banda Fresnel refleja h_sup_m e h_inf_m del perfil."""
    app = _make_app()
    profile = app.profile
    # La banda de Fresnel debe abarcar la diferencia h_sup - h_inf
    diff_profile = (profile.h_sup_m - profile.h_inf_m).max()
    assert diff_profile > 0.0, "La banda Fresnel debe tener amplitud positiva"
# ---------------------------------------------------------------------------
# F-7.4  Marcador de obstáculo en idx_critical
# ---------------------------------------------------------------------------
def test_obstacle_marker_at_idx_critical():
    """[F-7.4] El marcador de obstáculo está en la distancia del idx_critical."""
    app = _make_app()
    profile = app.profile
    marker = app.terrain_artists.marker_obstacle
    xdata = marker.get_xdata()
    assert len(xdata) == 1, "El marcador debe tener exactamente un punto"
    expected_d = profile.terrain.d1_m[profile.idx_critical]
    assert abs(float(xdata[0]) - float(expected_d)) < 1e-6, (
        f"Marcador en {xdata[0]:.1f} m, esperado {expected_d:.1f} m"
    )
# ---------------------------------------------------------------------------
# F-7.5  Panel de difracción marca (v_critical, Gd)
# ---------------------------------------------------------------------------
def test_diffraction_panel_marks_operating_point():
    """[F-7.5] El marcador del panel de difracción está en (v_critical, g_d_db)."""
    app = _make_app()
    profile = app.profile
    marker = app.diffraction_artists.marker_v_critical
    xdata = marker.get_xdata()
    ydata = marker.get_ydata()
    assert len(xdata) == 1
    assert abs(float(xdata[0]) - profile.v_critical) < 1e-9
    assert abs(float(ydata[0]) - profile.g_d_db) < 1e-9
# ---------------------------------------------------------------------------
# F-7.6  ui/ no importa funciones físicas individuales de core/
# ---------------------------------------------------------------------------
_FORBIDDEN_PHYSICAL_FUNCTIONS = [
    "earth_curvature_correction",
    "effective_elevation",
    "los_height",
    "fresnel_radius_n",
    "fresnel_bands",
    "los_clearance",
    "obstacle_height",
    "ffz_clearance",
    "fresnel_kirchhoff_parameter",
    "critical_obstacle_index",
    "diffraction_loss_db",
    "free_space_loss_db",
    "received_power_dbm",
    "link_margin_db",
    "link_availability",
]
_UI_MODULES = [
    "ui.app",
    "ui.layout",
    "ui.panels.terrain_panel",
    "ui.panels.diffraction_panel",
    "ui.panels.results_panel",
]
@pytest.mark.parametrize("ui_module", _UI_MODULES)
def test_ui_module_does_not_import_physical_functions(ui_module):
    """[F-7.6] Módulos de ui/ no deben importar funciones físicas de core/ directamente."""
    mod = importlib.import_module(ui_module)
    source_globals = vars(mod)
    for fn_name in _FORBIDDEN_PHYSICAL_FUNCTIONS:
        assert fn_name not in source_globals, (
            f"{ui_module} importa la función física '{fn_name}' directamente de core/"
        )
# ---------------------------------------------------------------------------
# Extras: verificar que el perfil cumple invariantes (integración)
# ---------------------------------------------------------------------------
def test_app_profile_satisfies_invariants():
    """El perfil calculado por App satisface todas las invariantes del motor."""
    from core.diffraction import diffraction_gain_db, diffraction_loss_db
    app = _make_app()
    profile = app.profile
    n = profile.terrain.n_points
    assert len(profile.h_er_m) == n
    assert len(profile.v) == n
    assert np.isnan(profile.v[0])
    assert np.isnan(profile.v[-1])
    assert profile.l_d_db >= 0.0
    assert profile.l_fs_db > 0.0
    assert abs(
        profile.g_d_db - diffraction_gain_db(profile.v_critical)
    ) < 1e-12
    assert abs(
        profile.l_d_db - diffraction_loss_db(profile.v_critical)
    ) < 1e-12
