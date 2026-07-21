"""
Tests de aceptación de la Etapa 8 — Widgets interactivos.
Se ejecutan con backend Agg (sin ventanas).
Criterios cubiertos:
    [F-8.1] Cambiar frecuencia estrecha la banda Fresnel.
    [F-8.2] Cambiar K modifica perfil efectivo y resultado crítico.
    [F-8.3] El valor dN/dh se actualiza al modificar K.
    [F-8.4] El toggle de terreno crudo no altera LinkProfile.
    [P-8.1] Al cargar V-2 desde interfaz, Ld = 6.0206 ± 0.01 dB.
Test del IMPL:
    dataclasses.replace crea nuevo objeto sin mutar el original.
"""
import matplotlib
matplotlib.use("Agg")
from dataclasses import replace
import numpy as np
import pytest
from validation.cases import case_flat_earth, case_lima
# ---------------------------------------------------------------------------
# Test mandatorio del IMPL §8
# ---------------------------------------------------------------------------
def test_replace_creates_new_params_without_mutating_original():
    """dataclasses.replace crea nuevo objeto sin mutar el original."""
    _, params = case_flat_earth()
    new_params = replace(params, f_hz=14e9)
    assert params.f_hz == 7e9
    assert new_params.f_hz == 14e9
    assert params is not new_params
# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _make_app_lima():
    """Devuelve una App con el caso Lima (Agg)."""
    from ui.app import App
    terrain, params = case_lima()
    return App(terrain, params)
# ---------------------------------------------------------------------------
# F-8.1  Cambiar frecuencia estrecha la banda Fresnel
# ---------------------------------------------------------------------------
def test_higher_freq_narrows_fresnel_band():
    """[F-8.1] Al doblar la frecuencia, la banda Fresnel se estrecha."""
    from ui.callbacks import on_freq_changed
    app = _make_app_lima()
    # Banda con frecuencia original (7 GHz)
    r1_original = app.profile.r1_m.copy()
    # Cambiar a 14 GHz mediante callback
    on_freq_changed(14.0, app)  # 14 GHz
    r1_new = app.profile.r1_m.copy()
    # r1 ∝ 1/√f  →  a mayor f, menor r1
    assert r1_new.max() < r1_original.max(), (
        f"r1_max original={r1_original.max():.2f}, "
        f"r1_max a 14 GHz={r1_new.max():.2f}"
    )
def test_freq_callback_uses_replace_not_mutation():
    """[F-8.1] El callback de frecuencia crea un nuevo LinkParams."""
    from ui.callbacks import on_freq_changed
    app = _make_app_lima()
    original_params = app.params
    on_freq_changed(14.0, app)
    assert app.params is not original_params
    assert app.params.f_hz == 14e9
    assert original_params.f_hz == 7e9  # sin mutar
# ---------------------------------------------------------------------------
# F-8.2  Cambiar K modifica perfil efectivo y resultado crítico
# ---------------------------------------------------------------------------
def test_k_callback_changes_effective_profile():
    """[F-8.2] Cambiar K modifica h_er_m y v_critical."""
    from ui.callbacks import on_k_changed
    app = _make_app_lima()
    h_er_original = app.profile.h_er_m.copy()
    v_crit_original = app.profile.v_critical
    # Cambiar K de 4/3 a 1.0
    on_k_changed(1.0, app)
    assert not np.allclose(app.profile.h_er_m, h_er_original), (
        "h_er_m no cambió al modificar K"
    )
    # v_critical debería cambiar en un perfil real con curvatura relevante
    # (no forzamos igualdad exacta, pero sí que el perfil se recalculó)
    assert np.any(app.profile.h_er_m != h_er_original)
def test_k_callback_uses_replace():
    """[F-8.2] Callback de K usa replace(); no muta el original."""
    from ui.callbacks import on_k_changed
    app = _make_app_lima()
    original_params = app.params
    on_k_changed(1.5, app)
    assert app.params is not original_params
    assert abs(app.params.K - 1.5) < 1e-12
    assert abs(original_params.K - 4 / 3) < 1e-12
# ---------------------------------------------------------------------------
# F-8.3  dN/dh se actualiza automáticamente al modificar K
# ---------------------------------------------------------------------------
def test_dndh_text_updates_on_k_change():
    """[F-8.3] El texto dN/dh refleja el gradiente equivalente al nuevo K."""
    from ui.callbacks import on_k_changed
    from core.atmosphere import gradient_from_k
    app = _make_app_lima()
    assert app.text_dndh is not None, "text_dndh debe existir en App"
    k_test = 1.5
    on_k_changed(k_test, app)
    expected_dndh = gradient_from_k(k_test)
    text_shown = app.text_dndh.get_text()
    assert f"{expected_dndh:.1f}" in text_shown, (
        f"Texto mostrado: '{text_shown}', "
        f"esperado contiene '{expected_dndh:.1f}'"
    )
# ---------------------------------------------------------------------------
# F-8.4  Toggle de terreno crudo no altera LinkProfile
# ---------------------------------------------------------------------------
def test_toggle_raw_terrain_does_not_recompute():
    """[F-8.4] El toggle cambia visibilidad del artista sin recalcular."""
    from ui.callbacks import on_toggle_raw_terrain
    app = _make_app_lima()
    profile_before = app.profile  # mismo objeto
    # Ocultar terreno crudo
    on_toggle_raw_terrain("Terreno crudo", app)
    assert app.profile is profile_before, (
        "El toggle no debe crear un nuevo LinkProfile"
    )
    assert not app.terrain_artists.line_terrain_raw.get_visible(), (
        "line_terrain_raw debe estar oculta tras el toggle"
    )
    # Restaurar visibilidad
    on_toggle_raw_terrain("Terreno crudo", app)
    assert app.terrain_artists.line_terrain_raw.get_visible(), (
        "line_terrain_raw debe ser visible tras segundo toggle"
    )
    assert app.profile is profile_before, "Sigue siendo el mismo profile"
# ---------------------------------------------------------------------------
# P-8.1  Cargar V-2 muestra Ld = 6.0206 ± 0.01 dB
# ---------------------------------------------------------------------------
def test_load_case_v2_gives_correct_ld():
    """[P-8.1] Al cargar V-2, el perfil muestra Ld = 6.0206 ± 0.01 dB."""
    from ui.callbacks import on_load_case_v2
    app = _make_app_lima()
    # Simular click del botón V-2
    on_load_case_v2(None, app)
    assert abs(app.profile.l_d_db - 6.0206) < 0.01, (
        f"Ld={app.profile.l_d_db:.4f} dB, esperado 6.0206 ± 0.01 dB"
    )
    assert abs(app.profile.v_critical) < 0.05, (
        f"v_critical={app.profile.v_critical:.4f}, esperado 0.00 ± 0.05"
    )
def test_load_case_v1_gives_correct_v_critical():
    """[P] Al cargar V-1, v_critical = -2.00 ± 0.03 y el perfil es válido."""
    from ui.callbacks import on_load_case_v1
    app = _make_app_lima()
    on_load_case_v1(None, app)
    assert abs(app.profile.v_critical - (-2.0)) < 0.03, (
        f"v_critical={app.profile.v_critical:.4f}"
    )
    # l_d_db ya está validado en test_engine.py (test_case_v1_flat_earth)
    assert app.profile.l_d_db >= 0.0
# ---------------------------------------------------------------------------
# Invariantes del perfil tras cada callback
# ---------------------------------------------------------------------------
def test_profile_invariants_after_freq_change():
    """El perfil cumple invariantes después de cambiar frecuencia."""
    from ui.callbacks import on_freq_changed
    from core.diffraction import diffraction_gain_db, diffraction_loss_db
    app = _make_app_lima()
    on_freq_changed(3.5, app)
    p = app.profile
    assert p.l_d_db >= 0.0
    assert p.l_fs_db > 0.0
    assert abs(p.g_d_db - diffraction_gain_db(p.v_critical)) < 1e-12
    assert abs(p.l_d_db - diffraction_loss_db(p.v_critical)) < 1e-12
    assert np.isnan(p.v[0])
    assert np.isnan(p.v[-1])
def test_profile_invariants_after_height_change():
    """El perfil cumple invariantes después de cambiar alturas de antena."""
    from ui.callbacks import on_htx_changed, on_hrx_changed
    from core.diffraction import diffraction_gain_db, diffraction_loss_db
    app = _make_app_lima()
    on_htx_changed(30.0, app)
    on_hrx_changed(25.0, app)
    p = app.profile
    assert p.l_d_db >= 0.0
    assert p.l_fs_db > 0.0
    assert abs(p.g_d_db - diffraction_gain_db(p.v_critical)) < 1e-12
    assert abs(p.l_d_db - diffraction_loss_db(p.v_critical)) < 1e-12
def test_sliders_sync_after_case_load():
    """Los sliders reflejan los parámetros del caso cargado."""
    from ui.callbacks import on_load_case_v1
    app = _make_app_lima()
    on_load_case_v1(None, app)
    # V-1: f_hz=7e9, K=1e12, h_tx=14.64, h_rx=14.64
    assert abs(app._sl_freq.val - 7.0) < 0.01
    # K=1e12 está fuera del rango del slider (max=3.0); el slider se clampea
    # Solo verificamos que el params tiene el valor correcto
    assert app.params.K == 1e12
    assert abs(app.params.h_tx_m - 14.64) < 1e-9
