"""
RadioLink LOS — Punto de entrada principal.

Versión: 1.1
Referencia: ARCH v1.1, §4 (main.py).

Punto de entrada de la aplicación. Parsea argumentos de línea de comandos
y lanza la interfaz gráfica.
"""

import argparse
import sys

from config.defaults import DEFAULT_PROFILE
from data.loader import load_terrain_csv
from ui.app import App


def main() -> None:
    """Punto de entrada del evaluador de radioenlace LOS."""
    parser = argparse.ArgumentParser(
        description="RadioLink LOS v1.1 - Evaluador de radioenlace"
    )
    parser.add_argument(
        "--profile",
        type=str,
        default=DEFAULT_PROFILE,
        help=f"Ruta al archivo CSV del perfil de terreno (por defecto: {DEFAULT_PROFILE})",
    )
    parser.add_argument(
        "--source",
        type=str,
        choices=["local", "api"],
        default="local",
        help="Fuente de datos del terreno (local o api).",
    )

    args = parser.parse_args()

    if args.source == "api":
        print("Error: La descarga por API (Etapa 11) aún no está implementada en este MVP (Etapa 8).")
        print("Por favor, usa '--source local' (por defecto).")
        sys.exit(1)


    try:
        terrain = load_terrain_csv(args.profile)
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo de perfil '{args.profile}'.")
        sys.exit(1)
    except Exception as e:
        print(f"Error al cargar el perfil de terreno: {e}")
        sys.exit(1)
    print(f"RadioLink LOS v1.1 - Iniciando con perfil: {args.profile}")
    app = App(terrain)
    app.show()


if __name__ == "__main__":
    main()
