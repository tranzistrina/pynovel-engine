from __future__ import annotations
from typing import Any

from .controller import MapController
from .interaction import MapInteraction
from .playable import PlayableMap
from .surface import MapSurface


class MapScene:
    """Runtime scene that presents a PlayableMap through a MapSurface."""
    def __init__(self, game_map: PlayableMap, viewport: Any, *, pygame_module: Any = None, emit=None):
        import pygame
        self.world = game_map
        self.definition = game_map.world.definition
        self.viewport = viewport if isinstance(viewport, pygame.Rect) else pygame.Rect(*viewport)
        self.pygame = pygame_module or pygame
        self.surface = MapSurface(self.definition, self.viewport)
        self.emit = emit or (lambda name, data: None)
        self.controller = MapController(self.surface, emit=self.emit)
        self.interaction = MapInteraction(self.controller, emit=self._emit_action)

    @property
    def map_world(self):
        return self.world.world

    def _emit_action(self, action: Any) -> None:
        self.emit(action.name, {"target_id": action.target_id, **action.data})

    def enter(self) -> None: pass
    def exit(self) -> None: pass
    def pause(self) -> None: pass
    def resume(self) -> None: pass
    def handle_input(self, event: Any) -> bool:
        if event.type == self.pygame.MOUSEBUTTONDOWN:
            if event.button == 2: self.interaction.begin_pan(event.pos); return True
            if event.button in (4, 5): self.controller.zoom(1.1 if event.button == 4 else 1 / 1.1, event.pos); return True
            return bool(self.interaction.pointer_down(event.pos, event.button, getattr(event, "timestamp", 0)))
        if event.type == self.pygame.MOUSEMOTION: self.interaction.move_pan(event.pos); return True
        if event.type == self.pygame.MOUSEBUTTONUP and event.button == 2: self.interaction.end_pan(); return True
        return False
    def update(self, dt: float) -> None: self.world.update(dt)
    def render(self, target: Any) -> None:
        self.surface.draw(target)
        for entity in self.map_world.entities.all():
            point=self.surface.map_to_screen(entity.position); self.pygame.draw.circle(target,(230,80,80),point,12)
    def serialize(self) -> dict[str, Any]: return self.world.serialize()
    def deserialize(self,payload: dict[str, Any]) -> None: self.world.deserialize(payload)
