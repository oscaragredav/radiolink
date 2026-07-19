"""
Tests de aceptación de la Etapa 1 — Carga de CSV y validaciones.

Criterios:
  [F-1.1] validation_flat.csv se carga correctamente.
  [F-1.2] Un CSV no monótono lanza TerrainLoadError.
  [P-1.1] d2_m[100] == 5_000.0 m.
"""

import numpy as np
import pandas as pd
import pytest

from data.loader import TerrainLoadError, load_terrain_csv, save_terrain_csv
from models.terrain import TerrainData


def test_load_validation_flat():
    """[F-1.1] validation_flat.csv se carga con 201 puntos y d_total=10000m."""
    terrain = load_terrain_csv("data/profiles/validation_flat.csv")

    assert terrain.n_points == 201
    assert terrain.d_total_m == 10_000.0
    assert terrain.d2_m[0] == 10_000.0
    assert terrain.d2_m[-1] == 0.0


def test_d2_m_at_center():
    """[P-1.1] d2_m en el punto central (índice 100) es 5000 m."""
    terrain = load_terrain_csv("data/profiles/validation_flat.csv")

    assert abs(terrain.d2_m[100] - 5_000.0) < 1e-12


def test_invalid_non_monotonic_csv_raises(tmp_path):
    """[F-1.2] Un CSV con distance_m no monótono lanza TerrainLoadError."""
    bad_path = tmp_path / "bad.csv"

    pd.DataFrame(
        {
            "distance_m": [0.0] + [float(i * 100) for i in range(1, 50)] + [50.0],
            "latitude": [0.0] * 51,
            "longitude": [0.0] * 51,
            "elevation_m": [0.0] * 51,
        }
    ).to_csv(bad_path, index=False)

    with pytest.raises(TerrainLoadError):
        load_terrain_csv(str(bad_path))


def test_invalid_too_few_points_raises(tmp_path):
    """Un CSV con menos de 50 puntos lanza TerrainLoadError."""
    bad_path = tmp_path / "short.csv"

    pd.DataFrame(
        {
            "distance_m": [float(i * 100) for i in range(10)],
            "latitude": [0.0] * 10,
            "longitude": [0.0] * 10,
            "elevation_m": [0.0] * 10,
        }
    ).to_csv(bad_path, index=False)

    with pytest.raises(TerrainLoadError):
        load_terrain_csv(str(bad_path))


def test_invalid_nonzero_start_raises(tmp_path):
    """Un CSV donde distance_m[0] != 0 lanza TerrainLoadError."""
    bad_path = tmp_path / "nonzero.csv"

    pd.DataFrame(
        {
            "distance_m": [float(i * 100 + 10) for i in range(60)],
            "latitude": [0.0] * 60,
            "longitude": [0.0] * 60,
            "elevation_m": [0.0] * 60,
        }
    ).to_csv(bad_path, index=False)

    with pytest.raises(TerrainLoadError):
        load_terrain_csv(str(bad_path))


def test_invalid_nan_elevation_raises(tmp_path):
    """Un CSV con NaN en elevation_m lanza TerrainLoadError."""
    bad_path = tmp_path / "nan_elev.csv"

    elev = [0.0] * 60
    elev[30] = float("nan")

    pd.DataFrame(
        {
            "distance_m": [float(i * 100) for i in range(60)],
            "latitude": [0.0] * 60,
            "longitude": [0.0] * 60,
            "elevation_m": elev,
        }
    ).to_csv(bad_path, index=False)

    with pytest.raises(TerrainLoadError):
        load_terrain_csv(str(bad_path))


def test_missing_columns_raises(tmp_path):
    """Un CSV sin columnas requeridas lanza TerrainLoadError."""
    bad_path = tmp_path / "missing.csv"

    pd.DataFrame(
        {
            "distance_m": [0.0, 100.0, 200.0],
            "elevation_m": [0.0, 0.0, 0.0],
        }
    ).to_csv(bad_path, index=False)

    with pytest.raises(TerrainLoadError):
        load_terrain_csv(str(bad_path))


def test_save_and_reload_terrain(tmp_path):
    """Un TerrainData guardado y recargado produce los mismos datos."""
    original = load_terrain_csv("data/profiles/validation_flat.csv")
    save_path = str(tmp_path / "roundtrip.csv")

    save_terrain_csv(original, save_path)
    reloaded = load_terrain_csv(save_path)

    assert reloaded.n_points == original.n_points
    assert reloaded.d_total_m == original.d_total_m
    assert np.allclose(reloaded.d1_m, original.d1_m)
    assert np.allclose(reloaded.elevation_m, original.elevation_m)


def test_validation_flat_elevation_is_zero():
    """El perfil plano de validación tiene elevación cero en todos los puntos."""
    terrain = load_terrain_csv("data/profiles/validation_flat.csv")

    assert np.all(terrain.elevation_m == 0.0)


def test_validation_flat_spacing_is_50m():
    """El perfil plano tiene espaciamiento uniforme de 50 m."""
    terrain = load_terrain_csv("data/profiles/validation_flat.csv")

    diffs = np.diff(terrain.d1_m)
    assert np.allclose(diffs, 50.0)


def test_load_validation_edge():
    """validation_edge.csv se carga correctamente (misma grilla que flat)."""
    terrain = load_terrain_csv("data/profiles/validation_edge.csv")

    assert terrain.n_points == 201
    assert terrain.d_total_m == 10_000.0
