"""
Constantes físicas universales del proyecto RadioLink LOS.

Todas las constantes están en unidades SI salvo donde se indica explícitamente.
Referencia: MATHSPEC v1.1, §1.
"""

# Velocidad de la luz en el vacío [m/s]
C_LIGHT: float = 3e8

# Radio medio de la Tierra [m]
R_EARTH: float = 6_371_000

# Radio medio de la Tierra [km]
R_EARTH_KM: float = 6_371.0

# Factor de escala terrestre estándar (atmósfera normal) [-]
K_STANDARD: float = 4 / 3

# Gradiente de refractividad estándar [N-units/km]
G_STANDARD: float = -39.0
