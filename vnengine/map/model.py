from __future__ import annotations
from dataclasses import dataclass, field
from math import floor
from typing import Any


@dataclass(frozen=True, slots=True)
class MapPoint:
    x: float
    y: float


@dataclass(frozen=True, slots=True)
class MapNode:
    id: str
    position: MapPoint
    label: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class MapConnection:
    source: str
    target: str
    cost: float = 1.0
    blocked: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class MapDefinition:
    width: float
    height: float
    background: str | None = None
    nodes: tuple[MapNode, ...] = ()
    connections: tuple[MapConnection, ...] = ()
    layers: tuple[dict[str, Any], ...] = ()
    areas: tuple[dict[str, Any], ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "MapDefinition":
        nodes = tuple(
            MapNode(str(raw["id"]), MapPoint(float(raw.get("x", 0)), float(raw.get("y", 0))), str(raw.get("label", "")), dict(raw.get("metadata", {})))
            for raw in payload.get("nodes", [])
        )
        connections = tuple(
            MapConnection(str(raw["source"]), str(raw["target"]), float(raw.get("cost", 1.0)), bool(raw.get("blocked", False)), dict(raw.get("metadata", {})))
            for raw in payload.get("connections", [])
        )
        return cls(
            float(payload.get("width", 0)), float(payload.get("height", 0)),
            payload.get("background"), nodes, connections,
            tuple(dict(item) for item in payload.get("layers", [])),
            tuple(dict(item) for item in payload.get("areas", [])),
            dict(payload.get("metadata", {})),
        )


@dataclass(slots=True)
class Camera2D:
    x: float = 0.0
    y: float = 0.0
    zoom: float = 1.0
    viewport_width: float = 1280.0
    viewport_height: float = 720.0

    def map_to_screen(self, point: MapPoint) -> MapPoint:
        return MapPoint((point.x - self.x) * self.zoom + self.viewport_width / 2, (point.y - self.y) * self.zoom + self.viewport_height / 2)

    def screen_to_map(self, point: MapPoint) -> MapPoint:
        return MapPoint((point.x - self.viewport_width / 2) / self.zoom + self.x, (point.y - self.viewport_height / 2) / self.zoom + self.y)

    def pan(self, dx: float, dy: float) -> None:
        self.x += dx / max(self.zoom, 1e-9); self.y += dy / max(self.zoom, 1e-9)

    def set_zoom(self, zoom: float, anchor: MapPoint | None = None) -> None:
        zoom = max(0.05, float(zoom))
        if anchor is not None:
            before = self.screen_to_map(anchor)
            self.zoom = zoom
            after = self.screen_to_map(anchor)
            self.x += before.x - after.x; self.y += before.y - after.y
        else:
            self.zoom = zoom

    def clamp(self, width: float, height: float) -> None:
        half_w = self.viewport_width / max(self.zoom, 1e-9) / 2
        half_h = self.viewport_height / max(self.zoom, 1e-9) / 2
        self.x = max(half_w, min(width - half_w, self.x)) if width >= 2 * half_w else width / 2
        self.y = max(half_h, min(height - half_h, self.y)) if height >= 2 * half_h else height / 2
