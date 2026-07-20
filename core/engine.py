"""
Motor orquestador del pipeline de cálculo de radioenlace.

Referencia: ARCH v1.1, §4 y §6 (core/engine.py).
Ecuaciones: MATHSPEC v1.1, EQ-04 a EQ-24.

``compute_link_profile`` es la única función del motor que usa la interfaz.
Ejecuta el pipeline completo V1 y retorna un ``LinkProfile`` inmutable
con todos los campos poblados y las invariantes verificadas.
"""

from typing import Optional

import numpy as np

from config.constants import C_LIGHT
from core.atmosphere import earth_curvature_correction, effective_elevation
from core.diffraction import (
    critical_obstacle_index,
    diffraction_gain_db,
    diffraction_loss_db,
    fresnel_kirchhoff_parameter,
)
from core.fresnel_zones import (
    ffz_clearance,
    fresnel_bands,
    fresnel_radius_n,
    los_clearance,
    obstacle_height,
)
from core.geometry import antenna_heights_msl, los_height
from core.link_budget import (
    free_space_loss_db,
    link_availability,
    link_margin_db,
    received_power_dbm,
)
from models.params import LinkParams, PowerBudgetParams
from models.profile import LinkProfile
from models.terrain import TerrainData


def compute_link_profile(
    params: LinkParams,
    terrain: TerrainData,
    pb_params: Optional[PowerBudgetParams] = None,
) -> LinkProfile:
    """Ejecuta el pipeline V1 completo y retorna un LinkProfile.

    Pipeline:
        1.  atmosphere.earth_curvature_correction -> h_er_m
        2.  atmosphere.effective_elevation -> z_eff_m
        3.  geometry.antenna_heights_msl -> H_Tx, H_Rx
        4.  geometry.los_height -> h_los_m
        5.  fresnel_zones.fresnel_radius_n -> r1_m
        6.  fresnel_zones.fresnel_bands -> h_sup_m, h_inf_m, h_60pct_m
        7.  fresnel_zones.los_clearance -> c_los_m
        8.  fresnel_zones.obstacle_height -> h_o_m
        9.  fresnel_zones.ffz_clearance -> c_ffz_m
        10. diffraction.fresnel_kirchhoff_parameter -> v
        11. diffraction.critical_obstacle_index -> idx_critical
        12. diffraction.diffraction_gain_db(v_critical) -> g_d_db
        13. diffraction.diffraction_loss_db(v_critical) -> l_d_db
        14. link_budget.free_space_loss_db -> l_fs_db
        15. Si pb_params no es None:
            link_budget.received_power_dbm -> p_rx_dbm
            link_budget.link_margin_db -> margin_db
            link_budget.link_availability -> availability_pct
        16. Verifica invariantes de LinkProfile.

    No importa ni ejecuta core.extensions en V1.

    Args:
        params:     Parámetros del enlace (LinkParams).
        terrain:    Datos del perfil de terreno (TerrainData).
        pb_params:  Parámetros del power budget (opcional).

    Returns:
        LinkProfile con todos los campos poblados.
    """
    # Longitud de onda
    lam_m = C_LIGHT / params.f_hz

    # --- Paso 1: Corrección por curvatura terrestre ---
    h_er_m = earth_curvature_correction(
        terrain.d1_m, terrain.d2_m, params.K
    )

    # --- Paso 2: Elevación efectiva ---
    z_eff_m = effective_elevation(terrain.elevation_m, h_er_m)

    # --- Paso 3: Alturas absolutas de antena ---
    H_tx_m, H_rx_m = antenna_heights_msl(
        z_tx_m=terrain.elevation_m[0],
        h_tx_m=params.h_tx_m,
        z_rx_m=terrain.elevation_m[-1],
        h_rx_m=params.h_rx_m,
    )

    # --- Paso 4: Línea de visión directa ---
    h_los_m = los_height(H_tx_m, H_rx_m, terrain.d1_m, terrain.d_total_m)

    # --- Paso 5: Radio de la primera zona de Fresnel ---
    r1_m = fresnel_radius_n(1, lam_m, terrain.d1_m, terrain.d2_m)

    # --- Paso 6: Bandas de Fresnel ---
    h_sup_m, h_inf_m, h_60pct_m = fresnel_bands(h_los_m, r1_m)

    # --- Paso 7: Despeje respecto a LOS ---
    c_los_m = los_clearance(h_los_m, z_eff_m)

    # --- Paso 8: Altura de obstáculo sobre LOS ---
    h_o_m = obstacle_height(c_los_m)

    # --- Paso 9: Despeje relativo al 60% de Fresnel ---
    c_ffz_m = ffz_clearance(c_los_m, r1_m)

    # --- Paso 10: Parámetro de Fresnel-Kirchhoff ---
    v = fresnel_kirchhoff_parameter(h_o_m, lam_m, terrain.d1_m, terrain.d2_m)

    # --- Paso 11: Obstáculo crítico ---
    idx_critical = critical_obstacle_index(v)
    v_critical = float(v[idx_critical])

    # --- Paso 12–13: Difracción ---
    g_d_db = diffraction_gain_db(v_critical)
    l_d_db = diffraction_loss_db(v_critical)

    # --- Paso 14: Pérdida en espacio libre ---
    l_fs_db = free_space_loss_db(terrain.d_total_m, params.f_hz)

    # --- Paso 15: Power budget (opcional) ---
    p_rx_dbm_val: Optional[float] = None
    margin_db_val: Optional[float] = None
    availability_pct_val: Optional[float] = None

    if pb_params is not None:
        p_rx_dbm_val = received_power_dbm(params, pb_params, l_fs_db, l_d_db)
        margin_db_val = link_margin_db(p_rx_dbm_val, pb_params.sensitivity_dbm)

        f_ghz = params.f_hz / 1e9
        d_km = terrain.d_total_m / 1e3
        availability_pct_val = link_availability(
            margin_db_val, f_ghz, d_km,
            pb_params.a_climate, pb_params.b_terrain,
        )

    # --- Paso 16: Construir y verificar LinkProfile ---
    profile = LinkProfile(
        params=params,
        terrain=terrain,
        h_er_m=h_er_m,
        z_eff_m=z_eff_m,
        h_los_m=h_los_m,
        r1_m=r1_m,
        h_sup_m=h_sup_m,
        h_inf_m=h_inf_m,
        h_60pct_m=h_60pct_m,
        c_los_m=c_los_m,
        h_o_m=h_o_m,
        c_ffz_m=c_ffz_m,
        v=v,
        idx_critical=idx_critical,
        v_critical=v_critical,
        g_d_db=g_d_db,
        l_d_db=l_d_db,
        l_fs_db=l_fs_db,
        p_rx_dbm=p_rx_dbm_val,
        margin_db=margin_db_val,
        availability_pct=availability_pct_val,
    )

    # Verificar invariantes
    _verify_invariants(profile)

    return profile


def _verify_invariants(profile: LinkProfile) -> None:
    """Verifica las postcondiciones del LinkProfile según ARCH §4.

    Lanza AssertionError si alguna invariante no se cumple.
    """
    n = profile.terrain.n_points

    # Todos los arrays tienen longitud N
    arrays = [
        profile.h_er_m, profile.z_eff_m, profile.h_los_m,
        profile.r1_m, profile.h_sup_m, profile.h_inf_m, profile.h_60pct_m,
        profile.c_los_m, profile.h_o_m, profile.c_ffz_m, profile.v,
    ]
    for arr in arrays:
        assert len(arr) == n, (
            f"Array tiene longitud {len(arr)}, esperado {n}"
        )

    # Curvatura cero en extremos
    assert profile.h_er_m[0] == 0.0, "h_er_m[0] debe ser 0.0"
    assert profile.h_er_m[-1] == 0.0, "h_er_m[-1] debe ser 0.0"

    # z_eff = elevation + h_er
    assert np.allclose(
        profile.z_eff_m,
        profile.terrain.elevation_m + profile.h_er_m,
    ), "z_eff_m != elevation_m + h_er_m"

    # Fresnel cero en extremos
    assert profile.r1_m[0] == 0.0, "r1_m[0] debe ser 0.0"
    assert profile.r1_m[-1] == 0.0, "r1_m[-1] debe ser 0.0"

    # v es NaN en extremos
    assert np.isnan(profile.v[0]), "v[0] debe ser NaN"
    assert np.isnan(profile.v[-1]), "v[-1] debe ser NaN"

    # Obstáculo crítico en rango interior
    assert 1 <= profile.idx_critical <= n - 2, (
        f"idx_critical={profile.idx_critical} fuera de [1, {n-2}]"
    )
    assert profile.idx_critical == np.nanargmax(profile.v), (
        "idx_critical no coincide con nanargmax(v)"
    )

    # v_critical coherente
    assert profile.v_critical == profile.v[profile.idx_critical], (
        "v_critical no coincide con v[idx_critical]"
    )

    # Difracción coherente
    assert abs(
        profile.g_d_db - diffraction_gain_db(profile.v_critical)
    ) < 1e-12, "g_d_db no coincide con diffraction_gain_db(v_critical)"

    assert abs(
        profile.l_d_db - diffraction_loss_db(profile.v_critical)
    ) < 1e-12, "l_d_db no coincide con diffraction_loss_db(v_critical)"

    # Restricciones de signo
    assert profile.l_d_db >= 0.0, "l_d_db debe ser >= 0"
    assert profile.l_fs_db > 0.0, "l_fs_db debe ser > 0"
