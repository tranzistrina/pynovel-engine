from __future__ import annotations
from dataclasses import dataclass
from math import hypot
from typing import Any
import pygame
from vnengine.map.model import Camera2D, MapDefinition, MapNode, MapPoint


@dataclass(slots=True)
class MapMarker:
    id: str
    position: MapPoint
    label: str = ""
    radius: float = 12.0
    metadata: dict[str, Any] | None = None
    visible: bool = True


class MapSurface:
    """Interactive map viewport built on top of MapDefinition and Camera2D."""

    def __init__(self, definition: MapDefinition, viewport: pygame.Rect | None = None):
        self.definition = definition
        self.viewport = viewport or pygame.Rect(0, 0, 1280, 720)
        self.camera = Camera2D(viewport_width=self.viewport.width, viewport_height=self.viewport.height)
        self.selected_id: str | None = None
        self.markers: dict[str, MapMarker] = {}
        self.route: list[str] = []
        self._drag_origin: tuple[int, int] | None = None
        self._camera_origin: tuple[float, float] | None = None

    def resize(self, rect: pygame.Rect) -> None:
        self.viewport = rect.copy(); self.camera.viewport_width = rect.width; self.camera.viewport_height = rect.height

    def add_marker(self, marker: MapMarker) -> None:
        if marker.id in self.markers: raise ValueError(f"Duplicate map marker: {marker.id}")
        self.markers[marker.id] = marker

    def remove_marker(self, marker_id: str) -> None:
        self.markers.pop(marker_id, None)
        if self.selected_id == marker_id: self.selected_id = None

    def set_route(self, node_ids: list[str]) -> None:
        known = {node.id for node in self.definition.nodes}
        missing = [node_id for node_id in node_ids if node_id not in known]
        if missing: raise ValueError(f"Unknown route nodes: {missing}")
        self.route = list(node_ids)

    def screen_to_map(self, pos: tuple[int, int]) -> MapPoint:
        local = MapPoint(pos[0] - self.viewport.x, pos[1] - self.viewport.y)
        return self.camera.screen_to_map(local)

    def map_to_screen(self, point: MapPoint) -> tuple[int, int]:
        p = self.camera.map_to_screen(point)
        return int(self.viewport.x + p.x), int(self.viewport.y + p.y)

    def hit_test(self, pos: tuple[int, int], radius: float = 18.0) -> MapNode | MapMarker | None:
        point = self.screen_to_map(pos)
        for marker in reversed(tuple(self.markers.values())):
            if marker.visible and hypot(point.x - marker.position.x, point.y - marker.position.y) <= radius / max(self.camera.zoom, 1e-9): return marker
        for node in self.definition.nodes:
            if hypot(point.x - node.position.x, point.y - node.position.y) <= radius / max(self.camera.zoom, 1e-9): return node
        return None

    def select_at(self, pos: tuple[int, int]) -> MapNode | MapMarker | None:
        hit = self.hit_test(pos)
        self.selected_id = getattr(hit, "id", None)
        return hit

    def begin_pan(self, pos: tuple[int, int]) -> None:
        self._drag_origin = pos; self._camera_origin = (self.camera.x, self.camera.y)

    def pan_to(self, pos: tuple[int, int]) -> None:
        if self._drag_origin is None or self._camera_origin is None: return
        dx = pos[0] - self._drag_origin[0]; dy = pos[1] - self._drag_origin[1]
        self.camera.x = self._camera_origin[0] - dx / max(self.camera.zoom, 1e-9)
        self.camera.y = self._camera_origin[1] - dy / max(self.camera.zoom, 1e-9)
        self.camera.clamp(self.definition.width, self.definition.height)

    def end_pan(self) -> None:
        self._drag_origin = None; self._camera_origin = None

    def zoom_at(self, factor: float, pos: tuple[int, int]) -> None:
        local = MapPoint(pos[0] - self.viewport.x, pos[1] - self.viewport.y)
        self.camera.set_zoom(self.camera.zoom * factor, local); self.camera.clamp(self.definition.width, self.definition.height)

    def draw(self, surface: pygame.Surface, node_radius: int = 8) -> None:
        old_clip = surface.get_clip(); surface.set_clip(self.viewport)
        if self.definition.background:
            try: surface.blit(pygame.image.load(self.definition.background).convert(), self.viewport)
            except (pygame.error, FileNotFoundError): pass
        for connection in self.definition.connections:
            if connection.blocked: continue
            a = next((n for n in self.definition.nodes if n.id == connection.source), None); b = next((n for n in self.definition.nodes if n.id == connection.target), None)
            if a and b: pygame.draw.line(surface, (100, 100, 100), self.map_to_screen(a.position), self.map_to_screen(b.position), max(1, int(self.camera.zoom)))
        for node in self.definition.nodes:
            p = self.map_to_screen(node.position); r = max(3, int(node_radius * self.camera.zoom))
            pygame.draw.circle(surface, (220, 220, 220), p, r)
            if node.id == self.selected_id: pygame.draw.circle(surface, (255, 220, 80), p, r + 4, 2)
        if len(self.route) > 1:
            lookup = {n.id: n for n in self.definition.nodes}
            points = [self.map_to_screen(lookup[n].position) for n in self.route if n in lookup]
            if len(points) > 1: pygame.draw.lines(surface, (255, 180, 60), False, points, max(2, int(3 * self.camera.zoom)))
        for marker in self.markers.values():
            if not marker.visible: continue
            p = self.map_to_screen(marker.position); r = max(3, int(marker.radius * self.camera.zoom))
            pygame.draw.circle(surface, (80, 180, 255), p, r)
            if marker.id == self.selected_id: pygame.draw.circle(surface, (255, 220, 80), p, r + 4, 2)
        surface.set_clip(old_clip)
