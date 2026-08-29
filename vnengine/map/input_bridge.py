from __future__ import annotations
from typing import Any
from .model import MapPoint
from .playable import PlayableMap
from .surface import MapSurface


class PlayableMapInput:
    """Connects screen-space clicks to PlayableMap selection and movement."""
    def __init__(self, game_map: PlayableMap, surface: MapSurface, emit=None):
        self.game_map = game_map
        self.surface = surface
        self.emit = emit or (lambda name, data: None)

    def click(self, screen_position: tuple[int, int], *, additive: bool = False):
        map_position = self.surface.screen_to_map(MapPoint(float(screen_position[0]), float(screen_position[1])))
        hit = self.game_map.select_at(map_position, additive=additive)
        self.emit("map.input_click", {"screen": screen_position, "map": map_position, "entity_id": hit.entity_id, "node_id": hit.node_id})
        return hit

    def move_click(self, screen_position: tuple[int, int], *, speed: float = 100.0):
        map_position = self.surface.screen_to_map(MapPoint(float(screen_position[0]), float(screen_position[1])))
        hit = self.game_map.hit_test(map_position)
        if hit.node_id is None:
            return None
        return self.game_map.move_selected(hit.node_id, speed)
