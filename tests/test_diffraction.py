import numpy as np
from scipy.special import fresnel as scipy_fresnel

from config.constants import C_LIGHT
from core.diffraction import (
    critical_obstacle_index,
    diffraction_function,
    diffraction_gain_db,
    diffraction_loss_db,
    fresnel_kirchhoff_parameter,
)


def test_diffraction_exact_value_at_v_zero():
    F0 = diffraction_function(0.0)
    g_d_db = diffraction_gain_db(0.0)
    l_d_db = diffraction_loss_db(0.0)

    error_f0 = abs(abs(F0) - 0.5)
    tolerance_f0 = 1e-6
    assert error_f0 < tolerance_f0

    error_gd = abs(g_d_db - (-6.0206))
    tolerance_gd = 0.01
    assert error_gd < tolerance_gd

    error_ld = abs(l_d_db - 6.0206)
    tolerance_ld = 0.01
    assert error_ld < tolerance_ld


def test_diffraction_function_matches_manual_construction_at_zero():
    S0, C0 = scipy_fresnel(0.0)

    F0_manual = (1.0 + 1.0j) / 2.0 * (
        (0.5 - C0) - 1.0j * (0.5 - S0)
    )

    error = abs(abs(F0_manual) - 0.5)
    tolerance = 1e-10
    assert error < tolerance


def test_v_sign_convention():
    lam_m = C_LIGHT / 7e9
    d1_m = np.array([np.nan, 4_000.0, np.nan])
    d2_m = np.array([np.nan, 6_000.0, np.nan])

    h_o_obstructed_m = np.array([np.nan, 50.0, np.nan])
    h_o_clear_m = np.array([np.nan, -20.0, np.nan])

    v_obstructed = fresnel_kirchhoff_parameter(
        h_o_obstructed_m,
        lam_m,
        d1_m,
        d2_m,
    )

    v_clear = fresnel_kirchhoff_parameter(
        h_o_clear_m,
        lam_m,
        d1_m,
        d2_m,
    )

    val_obstructed = v_obstructed[1]
    assert val_obstructed > 0.0
    val_clear = v_clear[1]
    assert val_clear < 0.0


def test_v_is_nan_at_endpoints():
    lam_m = C_LIGHT / 7e9
    d1_m = np.array([0.0, 4_000.0, 10_000.0])
    d2_m = np.array([10_000.0, 6_000.0, 0.0])
    h_o_m = np.array([0.0, 50.0, 0.0])

    v = fresnel_kirchhoff_parameter(h_o_m, lam_m, d1_m, d2_m)

    val_start = v[0]
    val_end = v[-1]
    assert np.isnan(val_start)
    assert np.isnan(val_end)


def test_critical_obstacle_is_selected_by_v():
    lam_m = C_LIGHT / 7e9
    d1_m = np.array([np.nan, 1_000.0, 5_000.0, np.nan])
    d2_m = np.array([np.nan, 9_000.0, 5_000.0, np.nan])
    h_o_m = np.array([np.nan, 100.0, 50.0, np.nan])

    v = fresnel_kirchhoff_parameter(h_o_m, lam_m, d1_m, d2_m)

    idx = critical_obstacle_index(v)
    expected_idx = np.nanargmax(v)
    assert idx == expected_idx


def test_diffraction_loss_is_never_negative():
    for value in np.linspace(-10.0, 10.0, 200):
        loss = diffraction_loss_db(float(value))
        assert loss >= 0.0
