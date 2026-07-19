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
    assert abs(K - 4 / 3) < 0.003


def test_gradient_from_standard_k():
    gradient = gradient_from_k(4 / 3)
    assert abs(gradient - (-39.0)) < 0.25


def test_earth_curvature_professor_example():
    d1_m = np.array([8_000.0])
    d2_m = np.array([12_000.0])
    h_er_m = earth_curvature_correction(d1_m, d2_m, 1.33)
    assert abs(h_er_m[0] - 5.666) < 0.05


def test_earth_curvature_is_zero_at_endpoints():
    d1_m = np.array([0.0, 5_000.0, 10_000.0])
    d2_m = np.array([10_000.0, 5_000.0, 0.0])
    h_er_m = earth_curvature_correction(d1_m, d2_m, K_STANDARD)
    assert h_er_m[0] == 0.0
    assert h_er_m[-1] == 0.0


def test_effective_elevation_does_not_include_antennas():
    z_raw_m = np.array([100.0, 120.0, 100.0])
    h_er_m = np.array([0.0, 5.0, 0.0])
    z_eff_m = effective_elevation(z_raw_m, h_er_m)
    assert np.allclose(z_eff_m, np.array([100.0, 125.0, 100.0]))
