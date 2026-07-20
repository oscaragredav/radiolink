import numpy as np

from config.constants import K_STANDARD
from core.atmosphere import (
    earth_curvature_correction,
    effective_elevation,
    gradient_from_k,
    k_from_gradient,
)


def test_standard_k_from_gradient():
    K = k_from_gradient(-39.0)
    error = abs(K - 4 / 3)
    tolerance = 0.003
    assert error < tolerance


def test_gradient_from_standard_k():
    gradient = gradient_from_k(4 / 3)
    error = abs(gradient - (-39.0))
    tolerance = 0.25
    assert error < tolerance


def test_earth_curvature_professor_example():
    d1_m = np.array([8_000.0])
    d2_m = np.array([12_000.0])
    h_er_m = earth_curvature_correction(d1_m, d2_m, 1.33)
    error = abs(h_er_m[0] - 5.666)
    tolerance = 0.05
    assert error < tolerance


def test_earth_curvature_is_zero_at_endpoints():
    d1_m = np.array([0.0, 5_000.0, 10_000.0])
    d2_m = np.array([10_000.0, 5_000.0, 0.0])
    h_er_m = earth_curvature_correction(d1_m, d2_m, K_STANDARD)
    val_start = h_er_m[0]
    val_end = h_er_m[-1]
    assert val_start == 0.0
    assert val_end == 0.0


def test_effective_elevation_does_not_include_antennas():
    z_raw_m = np.array([100.0, 120.0, 100.0])
    h_er_m = np.array([0.0, 5.0, 0.0])
    z_eff_m = effective_elevation(z_raw_m, h_er_m)
    expected_z = np.array([100.0, 125.0, 100.0])
    assert np.allclose(z_eff_m, expected_z)
