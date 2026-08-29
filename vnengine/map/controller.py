from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from vnengine.map.surface import MapSurface


@dataclass(frozen=True, slots=True)
class MapEvent:
    name: str
    target_id: str | None
    data: dict[str, Any]


class MapController:
    """Input-to-event bridge. The callback may be an EventBus emitter."""

    def __init__(self, surface: MapSurface, emit=None):
        self.surface = surface
        self.emit = emit or (lambda event: None)
        self._dragging = False

    def _publish(self, event: MapEvent) -> None:
        try:
            self.emit(event.name, {"target_id": event.target_id, **event.data})
        except TypeError:
            self.emit(event)

    def select(self, pos: tuple[int, int]) -> Any:
        hit = self.surface.select_at(pos)
        if hit is None:
            self._publish(MapEvent("map.selection_cleared", None, {}))
            return None
        event_name = "map.marker_selected" if hit.__class__.__name__ == "MapMarker" else "map.node_selected"
        self._publish(MapEvent(event_name, hit.id, {"object": hit}))
        return hit

    def begin_pan(self, pos: tuple[int, int]) -> None:
        self._dragging = True
        self.surface.begin_pan(pos)

    def move_pan(self, pos: tuple[int, int]) -> None:
        if self._dragging:
            self.surface.pan_to(pos)
            self._publish(MapEvent("map.camera_changed", None, {"x": self.surface.camera.x, "y": self.surface.camera.y, "zoom": self.surface.camera.zoom}))

    def end_pan(self) -> None:
        self._dragging = False
        self.surface.end_pan()

    def zoom(self, factor: float, pos: tuple[int, int]) -> None:
        self.surface.zoom_at(factor, pos)
        self._publish(MapEvent("map.camera_changed", None, {"x": self.surface.camera.x, "y": self.surface.camera.y, "zoom": self.surface.camera.zoom}))

    def set_route(self, node_ids: list[str]) -> None:
        self.surface.set_route(node_ids)
        self._publish(MapEvent("map.route_changed", None, {"nodes": list(node_ids)}))
