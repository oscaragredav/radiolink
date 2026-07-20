"""
Tests de aceptación de la Etapa 0 — Scaffolding del proyecto.

Criterios:
  [F-0.2] main.py ejecuta sin ImportError.
  [F-0.3] pytest -q ejecuta sin fallos.
  [P-0.1] R_EARTH == 6_371_000.
  [P-0.2] K_STANDARD == 4/3.
"""


def test_constants_exist():
    """[P-0.1] y [P-0.2]: constantes físicas con valores correctos."""
    from config.constants import K_STANDARD, R_EARTH

    r_earth_val = R_EARTH
    assert r_earth_val == 6_371_000

    error_k = abs(K_STANDARD - 4 / 3)
    tolerance_k = 1e-12
    assert error_k < tolerance_k


def test_main_importable():
    """[F-0.2]: main.py es importable sin errores."""
    import main

    assert main is not None


def test_defaults_importable():
    """Valores por defecto importables y coherentes."""
    from config.defaults import DEFAULT_FREQ_HZ, DEFAULT_K

    freq_val = DEFAULT_FREQ_HZ
    assert freq_val == 7e9

    error_k = abs(DEFAULT_K - 4 / 3)
    tolerance_k = 1e-12
    assert error_k < tolerance_k


def test_all_constants_defined():
    """Todas las constantes requeridas por ARCH §4 existen."""
    from config.constants import (
        C_LIGHT,
        G_STANDARD,
        K_STANDARD,
        R_EARTH,
        R_EARTH_KM,
    )

    c_light_val = C_LIGHT
    r_earth_val = R_EARTH
    r_earth_km_val = R_EARTH_KM
    g_standard_val = G_STANDARD

    assert c_light_val == 3e8
    assert r_earth_val == 6_371_000
    assert r_earth_km_val == 6_371.0

    error_k = abs(K_STANDARD - 4 / 3)
    tolerance_k = 1e-12
    assert error_k < tolerance_k

    assert g_standard_val == -39.0
