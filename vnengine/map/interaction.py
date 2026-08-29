from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from vnengine.map.controller import MapController, MapEvent


@dataclass(frozen=True, slots=True)
class MapAction:
    """Semantic action emitted from pointer interaction without game rules."""
    name: str
    target_id: str | None
    data: dict[str, Any]


class MapInteraction:
    """Small state machine for click, double-click, context-click and route gestures."""

    def __init__(self, controller: MapController, emit=None, double_click_ms: int = 350):
        self.controller = controller
        self.emit = emit or (lambda action: None)
        self.double_click_ms = double_click_ms
        self._last_click_ms = -10_000
        self._last_click_id: str | None = None
        self._route_start: str | None = None

    def pointer_down(self, pos: tuple[int, int], button: int, timestamp_ms: int) -> Any:
        if button == 3:
            hit = self.controller.surface.hit_test(pos)
            self.emit(MapAction("map.context_action", getattr(hit, "id", None), {"position": pos, "object": hit}))
            return hit
        if button != 1:
            return None
        hit = self.controller.select(pos)
        target_id = getattr(hit, "id", None)
        if target_id is not None and target_id == self._last_click_id and timestamp_ms - self._last_click_ms <= self.double_click_ms:
            self.emit(MapAction("map.double_click", target_id, {"object": hit}))
        self._last_click_ms = timestamp_ms
        self._last_click_id = target_id
        return hit

    def begin_pan(self, pos: tuple[int, int]) -> None:
        self.controller.begin_pan(pos)

    def move_pan(self, pos: tuple[int, int]) -> None:
        self.controller.move_pan(pos)

    def end_pan(self) -> None:
        self.controller.end_pan()

    def begin_route(self, node_id: str) -> None:
        self._route_start = node_id
        self.emit(MapAction("map.route_started", node_id, {"start": node_id}))

    def extend_route(self, node_id: str) -> None:
        if self._route_start is None:
            self.begin_route(node_id)
            return
        self.emit(MapAction("map.route_extended", node_id, {"start": self._route_start, "target": node_id}))

    def finish_route(self, node_ids: list[str]) -> None:
        self.controller.set_route(node_ids)
        self.emit(MapAction("map.route_created", None, {"nodes": list(node_ids)}))
        self._route_start = None

    def cancel_route(self) -> None:
        self._route_start = None
        self.emit(MapAction("map.route_cancelled", None, {}))
