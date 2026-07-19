"""
RadioLink LOS — Punto de entrada principal.

Versión: 1.1
Referencia: ARCH v1.1, §4 (main.py).

Este archivo es un stub para la Etapa 0. En etapas posteriores se
agregará el parseo de argumentos y la instanciación de la aplicación.
"""

from config.constants import (
    C_LIGHT,
    G_STANDARD,
    K_STANDARD,
    R_EARTH,
    R_EARTH_KM,
)
from config.defaults import (
    DEFAULT_FREQ_HZ,
    DEFAULT_H_RX_M,
    DEFAULT_H_TX_M,
    DEFAULT_K,
    DEFAULT_PROFILE,
    DEFAULT_SPACING_M,
)


def main() -> None:
    """Punto de entrada del evaluador de radioenlace LOS."""
    print("RadioLink LOS v1.1")
    print(f"  C_LIGHT      = {C_LIGHT:.3e} m/s")
    print(f"  R_EARTH      = {R_EARTH:.0f} m")
    print(f"  R_EARTH_KM   = {R_EARTH_KM:.1f} km")
    print(f"  K_STANDARD   = {K_STANDARD:.10f}")
    print(f"  G_STANDARD   = {G_STANDARD:.1f} N-units/km")
    print()
    print(f"  DEFAULT_FREQ = {DEFAULT_FREQ_HZ:.3e} Hz")
    print(f"  DEFAULT_H_TX = {DEFAULT_H_TX_M:.1f} m")
    print(f"  DEFAULT_H_RX = {DEFAULT_H_RX_M:.1f} m")
    print(f"  DEFAULT_K    = {DEFAULT_K:.10f}")
    print(f"  DEFAULT_SPACING = {DEFAULT_SPACING_M:.1f} m")
    print(f"  DEFAULT_PROFILE = {DEFAULT_PROFILE}")


if __name__ == "__main__":
    main()
