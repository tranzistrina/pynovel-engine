from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from .interaction import MapInteraction


@dataclass(frozen=True, slots=True)
class MapInputConfig:
    select_button: int = 1
    context_button: int = 3
    pan_button: int = 2
    zoom_step: float = 1.1


class MapInputAdapter:
    """Translates pygame events into semantic MapInteraction calls."""
    def __init__(self, interaction: MapInteraction, config: MapInputConfig | None = None):
        self.interaction = interaction
        self.config = config or MapInputConfig()
        self._panning = False

    def process(self, event: Any, timestamp_ms: int) -> bool:
        import pygame
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == self.config.pan_button:
                self._panning = True; self.interaction.begin_pan(event.pos); return True
            if event.button == 4:
                self.interaction.controller.zoom(self.config.zoom_step, event.pos); return True
            if event.button == 5:
                self.interaction.controller.zoom(1.0 / self.config.zoom_step, event.pos); return True
            self.interaction.pointer_down(event.pos, event.button, timestamp_ms); return event.button in (self.config.select_button, self.config.context_button)
        if event.type == pygame.MOUSEMOTION and self._panning:
            self.interaction.move_pan(event.pos); return True
        if event.type == pygame.MOUSEBUTTONUP and event.button == self.config.pan_button:
            self._panning = False; self.interaction.end_pan(); return True
        return False
