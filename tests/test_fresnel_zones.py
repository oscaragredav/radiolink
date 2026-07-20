import numpy as np

from config.constants import C_LIGHT
from core.fresnel_zones import (
    ffz_clearance,
    fresnel_bands,
    fresnel_radius_n,
    los_clearance,
    obstacle_height,
)


def test_fresnel_radius_professor_example():
    lam_m = C_LIGHT / 900e6
    d1_m = np.array([8_000.0])
    d2_m = np.array([12_000.0])

    r1_m = fresnel_radius_n(1, lam_m, d1_m, d2_m)

    error = abs(r1_m[0] - 39.986)
    tolerance = 0.05
    assert error < tolerance


def test_fresnel_radius_maximum_at_center():
    lam_m = C_LIGHT / 900e6
    d1_m = np.array([4_900.0, 5_000.0, 5_100.0])
    d2_m = 10_000.0 - d1_m

    r1_m = fresnel_radius_n(1, lam_m, d1_m, d2_m)

    val_center = r1_m[1]
    val_left = r1_m[0]
    val_right = r1_m[2]
    assert val_center >= val_left
    assert val_center >= val_right


def test_fresnel_radius_zero_at_endpoints():
    lam_m = C_LIGHT / 900e6
    d1_m = np.array([0.0, 5_000.0, 10_000.0])
    d2_m = 10_000.0 - d1_m

    r1_m = fresnel_radius_n(1, lam_m, d1_m, d2_m)

    val_start = r1_m[0]
    val_end = r1_m[-1]
    assert val_start == 0.0
    assert val_end == 0.0


def test_los_clearance_professor_example():
    h_los_m = np.array([126.0])
    z_eff_m = np.array([125.666])

    c_los_m = los_clearance(h_los_m, z_eff_m)

    error = abs(c_los_m[0] - 0.334)
    tolerance = 0.05
    assert error < tolerance


def test_ffz_clearance_professor_example():
    c_los_m = np.array([0.334])
    r1_m = np.array([39.986])

    c_ffz_m = ffz_clearance(c_los_m, r1_m)

    error = abs(c_ffz_m[0] - (-23.657))
    tolerance = 0.1
    assert error < tolerance


def test_obstacle_height_sign():
    c_los_m = np.array([0.334])

    h_o_m = obstacle_height(c_los_m)

    error = abs(h_o_m[0] - (-0.334))
    tolerance = 0.01
    assert error < tolerance


def test_fresnel_bands():
    h_los_m = np.array([100.0])
    r1_m = np.array([20.0])

    upper_m, lower_m, clearance_60_m = fresnel_bands(h_los_m, r1_m)

    val_upper = upper_m[0]
    val_lower = lower_m[0]
    val_clearance_60 = clearance_60_m[0]
    assert val_upper == 120.0
    assert val_lower == 80.0
    assert val_clearance_60 == 88.0
