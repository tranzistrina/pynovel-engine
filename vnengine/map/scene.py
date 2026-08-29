from __future__ import annotations
from typing import Any

from .playable import PlayableMap
from .surface import MapSurface


class MapScene:
    """Runtime scene that presents a PlayableMap through a MapSurface."""
    def __init__(self, game_map: PlayableMap, viewport: Any, *, pygame_module: Any = None):
        self.world = game_map
        self.viewport = viewport
        self.pygame = pygame_module
        self.surface = MapSurface(game_map.definition, viewport)
        self.input_adapter = None
        if pygame_module is not None:
            from .input import MapInputAdapter
            self.input_adapter = MapInputAdapter(self._interaction())

    def _interaction(self):
        class Interaction:
            begin_pan = self.surface.begin_pan
            move_pan = self.surface.pan_to
            end_pan = self.surface.end_pan
            pointer_down = lambda *_: False
            controller = type("Controller", (), {"zoom": lambda _, factor, pos: self.surface.zoom_at(factor, pos)})()
        return Interaction()

    def enter(self) -> None: pass
    def exit(self) -> None: pass
    def pause(self) -> None: pass
    def resume(self) -> None: pass

    def handle_input(self, event: Any) -> bool:
        if self.input_adapter is None: return False
        return bool(self.input_adapter.process(event))

    def update(self, dt: float) -> None:
        self.world.update(dt)

    def render(self, target: Any) -> None:
        self.surface.draw(target)
        if self.pygame is not None:
            for entity in self.world.entities.all():
                point = self.surface.map_to_screen(entity.position)
                self.pygame.draw.circle(target, (230, 80, 80), point, 12)

    def serialize(self) -> dict[str, Any]:
        return self.world.serialize()

    def deserialize(self, payload: dict[str, Any]) -> None:
        self.world.deserialize(payload)
