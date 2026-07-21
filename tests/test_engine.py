from dataclasses import replace

import numpy as np

from core.diffraction import diffraction_gain_db, diffraction_loss_db
from core.engine import compute_link_profile
from core.link_budget import free_space_loss_db
from validation.cases import case_edge_on_los, case_flat_earth, case_lima


def assert_profile_invariants(profile):
    """Verifica todas las invariantes de ARCH §4 en un LinkProfile."""
    terrain = profile.terrain
    n = terrain.n_points

    arrays = [
        profile.h_er_m,
        profile.z_eff_m,
        profile.h_los_m,
        profile.r1_m,
        profile.h_sup_m,
        profile.h_inf_m,
        profile.h_60pct_m,
        profile.c_los_m,
        profile.h_o_m,
        profile.c_ffz_m,
        profile.v,
    ]

    lengths = [len(a) for a in arrays]
    assert all(length == n for length in lengths)

    h_er_start = profile.h_er_m[0]
    h_er_end = profile.h_er_m[-1]
    assert h_er_start == 0.0
    assert h_er_end == 0.0

    z_eff_expected = terrain.elevation_m + profile.h_er_m
    assert np.allclose(profile.z_eff_m, z_eff_expected)

    r1_start = profile.r1_m[0]
    r1_end = profile.r1_m[-1]
    assert r1_start == 0.0
    assert r1_end == 0.0

    v_start = profile.v[0]
    v_end = profile.v[-1]
    assert np.isnan(v_start)
    assert np.isnan(v_end)

    idx = profile.idx_critical
    assert 1 <= idx <= n - 2

    expected_idx = np.nanargmax(profile.v)
    assert idx == expected_idx

    v_at_idx = profile.v[profile.idx_critical]
    assert profile.v_critical == v_at_idx

    g_d_expected = diffraction_gain_db(profile.v_critical)
    error_gd = abs(profile.g_d_db - g_d_expected)
    assert error_gd < 1e-12

    l_d_expected = diffraction_loss_db(profile.v_critical)
    error_ld = abs(profile.l_d_db - l_d_expected)
    assert error_ld < 1e-12

    assert profile.l_d_db >= 0.0
    assert profile.l_fs_db > 0.0

#caso tierra plana k infinito
def test_case_v1_flat_earth():
    terrain, params = case_flat_earth()
    profile = compute_link_profile(params, terrain)

    assert_profile_invariants(profile)

    error_v = abs(profile.v_critical - (-2.0))
    tolerance_v = 0.03
    assert error_v < tolerance_v

    # La función exacta de Fresnel para v ≈ -2.0 produce |F| ≈ 0.919
    # (la espiral de Cornu no ha convergido completamente a 1.0),
    # por lo que L_d es pequeña pero no cero. La expectativa L_d = 0.0
    # del IMPL asumía la aproximación de Lee (v ≤ -1 → G_d = 0), que
    # está descartada por D-01 y D-07 del MATHSPEC.
    l_d = profile.l_d_db
    assert l_d < 1.0

#caso tierra plana con terreno elevado a 2000m[80], k infinito
def test_case_v2_edge_on_los():
    terrain, params = case_edge_on_los()
    profile = compute_link_profile(params, terrain)

    assert_profile_invariants(profile)

    error_v = abs(profile.v_critical)
    tolerance_v = 0.05
    assert error_v < tolerance_v

    error_gd = abs(profile.g_d_db - (-6.0206))
    tolerance_gd = 0.01
    assert error_gd < tolerance_gd

    error_ld = abs(profile.l_d_db - 6.0206)
    tolerance_ld = 0.01
    assert error_ld < tolerance_ld

#caso lima: terreno plano considerando curvatura de la tierra
def test_case_v3_lima_internal_consistency():
    terrain, params = case_lima()
    profile = compute_link_profile(params, terrain)

    assert_profile_invariants(profile)

    expected_lfs_db = free_space_loss_db(
        terrain.d_total_m,
        params.f_hz,
    )

    error_lfs = abs(profile.l_fs_db - expected_lfs_db)
    tolerance_lfs = 0.01
    assert error_lfs < tolerance_lfs


def test_k_changes_result_for_lima():
    terrain, params = case_lima()

    profile_k1 = compute_link_profile(
        replace(params, K=1.0),
        terrain,
    )

    profile_kstandard = compute_link_profile(
        replace(params, K=4 / 3),
        terrain,
    )

    h_er_are_different = not np.allclose(
        profile_k1.h_er_m,
        profile_kstandard.h_er_m,
    )
    assert h_er_are_different

    v_k1 = profile_k1.v_critical
    v_kstd = profile_kstandard.v_critical
    assert v_k1 != v_kstd
