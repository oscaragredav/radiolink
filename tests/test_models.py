"""
Tests de aceptación de la Etapa 1 — Modelos de datos.

Criterios:
  [F-1.3] LinkParams no permite mutación directa.
"""

from dataclasses import FrozenInstanceError, replace

import numpy as np
import pytest

from models.params import LinkParams, PowerBudgetParams
from models.profile import LinkProfile
from models.terrain import TerrainData


def test_link_params_are_immutable():
    """[F-1.3] LinkParams no permite mutación directa."""
    params = LinkParams(
        f_hz=7e9,
        h_tx_m=10.0,
        h_rx_m=10.0,
        K=4 / 3,
    )

    with pytest.raises(FrozenInstanceError):
        params.K = 1.0


def test_power_budget_params_are_immutable():
    """PowerBudgetParams tampoco permite mutación directa."""
    pb = PowerBudgetParams(
        p_tx_dbm=40.0,
        g_tx_dbi=30.0,
        g_rx_dbi=30.0,
        l_cable_tx_db=1.0,
        l_cable_rx_db=1.0,
        sensitivity_dbm=-80.0,
        a_climate=0.5,
        b_terrain=1.0,
    )

    with pytest.raises(FrozenInstanceError):
        pb.p_tx_dbm = 50.0


def test_link_params_replace_creates_new_instance():
    """dataclasses.replace crea nueva instancia sin mutar la original."""
    params = LinkParams(
        f_hz=7e9,
        h_tx_m=10.0,
        h_rx_m=10.0,
        K=4 / 3,
    )

    new_params = replace(params, f_hz=14e9)

    assert params.f_hz == 7e9
    assert new_params.f_hz == 14e9
    assert params is not new_params


def test_terrain_data_properties():
    """TerrainData calcula d_total_m, d2_m y n_points correctamente."""
    d1 = np.array([0.0, 1000.0, 2000.0, 3000.0])
    terrain = TerrainData(
        d1_m=d1,
        lat=np.zeros(4),
        lon=np.zeros(4),
        elevation_m=np.zeros(4),
        source="test",
    )

    assert terrain.d_total_m == 3000.0
    assert terrain.n_points == 4
    assert np.allclose(terrain.d2_m, np.array([3000.0, 2000.0, 1000.0, 0.0]))


def test_link_profile_is_immutable():
    """LinkProfile no permite mutación directa."""
    n = 5
    dummy = np.zeros(n)
    terrain = TerrainData(
        d1_m=np.linspace(0, 1000, n),
        lat=np.zeros(n),
        lon=np.zeros(n),
        elevation_m=np.zeros(n),
        source="test",
    )
    params = LinkParams(f_hz=7e9, h_tx_m=10.0, h_rx_m=10.0, K=4 / 3)

    profile = LinkProfile(
        params=params,
        terrain=terrain,
        h_er_m=dummy,
        z_eff_m=dummy,
        h_los_m=dummy,
        r1_m=dummy,
        h_sup_m=dummy,
        h_inf_m=dummy,
        h_60pct_m=dummy,
        c_los_m=dummy,
        h_o_m=dummy,
        c_ffz_m=dummy,
        v=dummy,
        idx_critical=2,
        v_critical=0.0,
        g_d_db=-6.02,
        l_d_db=6.02,
        l_fs_db=130.0,
    )

    with pytest.raises(FrozenInstanceError):
        profile.l_d_db = 0.0


def test_link_profile_optional_fields_default_to_none():
    """Los campos de power budget son None por defecto."""
    n = 5
    dummy = np.zeros(n)
    terrain = TerrainData(
        d1_m=np.linspace(0, 1000, n),
        lat=np.zeros(n),
        lon=np.zeros(n),
        elevation_m=np.zeros(n),
        source="test",
    )
    params = LinkParams(f_hz=7e9, h_tx_m=10.0, h_rx_m=10.0, K=4 / 3)

    profile = LinkProfile(
        params=params,
        terrain=terrain,
        h_er_m=dummy,
        z_eff_m=dummy,
        h_los_m=dummy,
        r1_m=dummy,
        h_sup_m=dummy,
        h_inf_m=dummy,
        h_60pct_m=dummy,
        c_los_m=dummy,
        h_o_m=dummy,
        c_ffz_m=dummy,
        v=dummy,
        idx_critical=2,
        v_critical=0.0,
        g_d_db=-6.02,
        l_d_db=6.02,
        l_fs_db=130.0,
    )

    assert profile.p_rx_dbm is None
    assert profile.margin_db is None
    assert profile.availability_pct is None
