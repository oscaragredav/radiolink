"""
Controlador principal de la aplicación de visualización de radioenlace.

Versión estática (Etapa 7): construye la figura, los artistas y renderiza
el perfil inicial sin widgets interactivos.

Referencia: ARCH v1.1, §7.

La UI no recalcula física. Recibe un TerrainData y un LinkParams,
llama al motor una vez y actualiza todos los paneles con el LinkProfile.
"""

from __future__ import annotations

from typing import Optional

import matplotlib
from matplotlib.figure import Figure

from core.engine import compute_link_profile
from models.params import LinkParams, PowerBudgetParams
from models.terrain import TerrainData
from models.profile import LinkProfile
from ui.layout import build_figure
from ui.artists import build_terrain_artists, build_diffraction_artists, TerrainArtists, DiffractionArtists
from ui.panels.terrain_panel import draw_terrain_panel
from ui.panels.diffraction_panel import update_diffraction_panel
from ui.panels.results_panel import build_results_panel, update_results_panel


class App:
    """Controlador de la figura matplotlib.

    Etapa 7: versión estática sin widgets.

    Args:
        terrain:    Datos del perfil de terreno.
        params:     Parámetros del enlace (opcional; usa defaults de Lima si None).
        pb_params:  Parámetros de power budget (opcional).
    """

    def __init__(
        self,
        terrain: TerrainData,
        params: Optional[LinkParams] = None,
        pb_params: Optional[PowerBudgetParams] = None,
    ) -> None:
        # Parámetros por defecto si no se proporcionan
        if params is None:
            params = LinkParams(
                f_hz=7e9,
                h_tx_m=10.0,
                h_rx_m=10.0,
                K=4 / 3,
            )

        self.terrain = terrain
        self.params = params
        self.pb_params = pb_params

        # Construir figura y ejes
        self.fig, self.ax_terrain, self.ax_diffraction, self.ax_results = (
            build_figure()
        )

        # Crear artistas (una sola vez)
        self.terrain_artists: TerrainArtists = build_terrain_artists(
            self.ax_terrain
        )
        self.diffraction_artists: DiffractionArtists = (
            build_diffraction_artists(self.ax_diffraction)
        )
        self.result_texts = build_results_panel(self.ax_results)

        # Calcular perfil y dibujar
        self.profile: LinkProfile = compute_link_profile(
            self.params, self.terrain, self.pb_params
        )
        self._render(self.profile)

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def show(self) -> None:
        """Muestra la figura (bloquea si el backend lo requiere)."""
        import matplotlib.pyplot as plt
        plt.show()

    def save(self, path: str, dpi: int = 140) -> None:
        """Guarda la figura como imagen.

        Args:
            path: Ruta del archivo de salida (png, pdf, svg…).
            dpi:  Resolución de exportación.
        """
        self.fig.savefig(path, dpi=dpi, bbox_inches="tight",
                         facecolor=self.fig.get_facecolor())

    # ------------------------------------------------------------------
    # Métodos internos
    # ------------------------------------------------------------------

    def _render(self, profile: LinkProfile) -> None:
        """Actualiza todos los paneles con el perfil dado."""
        draw_terrain_panel(self.ax_terrain, self.terrain_artists, profile)
        update_diffraction_panel(
            self.ax_diffraction, self.diffraction_artists, profile
        )
        update_results_panel(self.result_texts, profile)
        self.fig.canvas.draw_idle()

    def _recompute(self) -> None:
        """Recalcula el perfil y actualiza la figura.

        Punto de entrada para los callbacks de la Etapa 8.
        """
        self.profile = compute_link_profile(
            self.params, self.terrain, self.pb_params
        )
        self._render(self.profile)
