import numpy as np

from config.constants import C_LIGHT
from core.link_budget import (
    free_space_loss_db,
    link_availability,
    link_margin_db,
    received_power_dbm,
)
from models.params import LinkParams, PowerBudgetParams


def build_params():
    return LinkParams(
        f_hz=7e9,
        h_tx_m=70.0,
        h_rx_m=90.0,
        K=4 / 3,
    )


def build_power_budget_params():
    return PowerBudgetParams(
        p_tx_dbm=40.0,
        g_tx_dbi=30.0,
        g_rx_dbi=30.0,
        l_cable_tx_db=1.0,
        l_cable_rx_db=1.0,
        sensitivity_dbm=-80.0,
        a_climate=0.5,
        b_terrain=1.0,
    )


def test_free_space_loss_professor_example():
    lam_m = C_LIGHT / 900e6
    expected_db = 20.0 * np.log10(4.0 * np.pi * 6_000.0 / lam_m)

    result_db = free_space_loss_db(6_000.0, 900e6)

    error = abs(result_db - expected_db)
    tolerance = 0.01
    assert error < tolerance


def test_free_space_loss_matches_ghz_km_expression():
    result_db = free_space_loss_db(6_000.0, 900e6)
    expected_db = 92.45 + 20.0 * np.log10(0.9) + 20.0 * np.log10(6.0)

    error = abs(result_db - expected_db)
    tolerance = 0.1
    assert error < tolerance


def test_received_power_without_diffraction_matches_manual_budget():
    params = build_params()
    pb = build_power_budget_params()

    l_fs_db = free_space_loss_db(20_000.0, 7e9)
    p_rx_dbm = received_power_dbm(params, pb, l_fs_db, 0.0)

    expected_dbm = 40.0 + 30.0 - 1.0 - l_fs_db + 30.0 - 1.0

    error = abs(p_rx_dbm - expected_dbm)
    tolerance = 0.01
    assert error < tolerance


def test_diffraction_loss_reduces_received_power_exactly():
    params = build_params()
    pb = build_power_budget_params()
    l_fs_db = free_space_loss_db(20_000.0, 7e9)

    p_rx_without_ld = received_power_dbm(params, pb, l_fs_db, 0.0)
    p_rx_with_ld = received_power_dbm(params, pb, l_fs_db, 10.0)

    difference = p_rx_without_ld - p_rx_with_ld
    error = abs(difference - 10.0)
    tolerance = 0.01
    assert error < tolerance


def test_link_margin():
    margin = link_margin_db(-70.0, -80.0)
    expected = 10.0
    assert margin == expected


def test_availability_increases_with_margin():
    a_20 = link_availability(20.0, 7.0, 20.0, 0.5, 1.0)
    a_30 = link_availability(30.0, 7.0, 20.0, 0.5, 1.0)

    assert a_30 > a_20
