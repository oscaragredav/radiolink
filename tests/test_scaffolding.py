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

    assert R_EARTH == 6_371_000
    assert abs(K_STANDARD - 4 / 3) < 1e-12


def test_main_importable():
    """[F-0.2]: main.py es importable sin errores."""
    import main

    assert main is not None


def test_defaults_importable():
    """Valores por defecto importables y coherentes."""
    from config.defaults import DEFAULT_FREQ_HZ, DEFAULT_K

    assert DEFAULT_FREQ_HZ == 7e9
    assert abs(DEFAULT_K - 4 / 3) < 1e-12


def test_all_constants_defined():
    """Todas las constantes requeridas por ARCH §4 existen."""
    from config.constants import (
        C_LIGHT,
        G_STANDARD,
        K_STANDARD,
        R_EARTH,
        R_EARTH_KM,
    )

    assert C_LIGHT == 3e8
    assert R_EARTH == 6_371_000
    assert R_EARTH_KM == 6_371.0
    assert abs(K_STANDARD - 4 / 3) < 1e-12
    assert G_STANDARD == -39.0
