"""
Valores por defecto de parámetros del enlace.

Referencia: ARCH v1.1, §4 (config/defaults.py).
"""

# Frecuencia por defecto [Hz]
DEFAULT_FREQ_HZ: float = 7e9

# Altura de mástil Tx por defecto [m]
DEFAULT_H_TX_M: float = 90.0

# Altura de mástil Rx por defecto [m]
DEFAULT_H_RX_M: float = 90.0

# Factor K por defecto [-]
DEFAULT_K: float = 4 / 3

# Espaciamiento entre puntos del perfil [m]
DEFAULT_SPACING_M: float = 50.0

# Ruta del perfil por defecto
DEFAULT_PROFILE: str = "data/profiles/lima1.csv" #Atocongo-San Bartolo
#TODO: Agregar perfil lima2.csv (La Molina-Chosica)
