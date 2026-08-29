from __future__ import annotations
from typing import Any
from vnengine.map.controller import MapController
from vnengine.map.interaction import MapInteraction
from vnengine.map.surface import MapSurface


class RuntimeMap:
    """Convenience adapter that connects a MapSurface to ExtensibleRuntime events."""

    def __init__(self, runtime, surface: MapSurface):
        self.runtime = runtime
        self.surface = surface
        self.controller = MapController(surface, runtime.emit)
        self.interaction = MapInteraction(self.controller, runtime.emit)

    def select(self, pos: tuple[int, int]) -> Any:
        return self.interaction.pointer_down(pos, 1, 0)

    def context(self, pos: tuple[int, int]) -> Any:
        return self.interaction.pointer_down(pos, 3, 0)

    def zoom(self, factor: float, pos: tuple[int, int]) -> None:
        self.controller.zoom(factor, pos)

    def set_route(self, node_ids: list[str]) -> None:
        self.controller.set_route(node_ids)

    def draw(self, surface) -> None:
        self.surface.draw(surface)
