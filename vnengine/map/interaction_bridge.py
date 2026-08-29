from __future__ import annotations
from typing import Any
from .model import MapPoint
from .playable import PlayableMap
from .surface import MapSurface


class PlayableInteractionBridge:
    """Turns semantic map clicks into selection and movement actions."""
    def __init__(self, game_map: PlayableMap, surface: MapSurface, speed: float = 100.0):
        self.game_map = game_map
        self.surface = surface
        self.speed = speed
        self.armed = False

    def select_click(self, screen_position: tuple[int, int], additive: bool = False):
        point = self.surface.screen_to_map(MapPoint(float(screen_position[0]), float(screen_position[1])))
        return self.game_map.select_at(point, additive=additive)

    def command_click(self, screen_position: tuple[int, int]):
        point = self.surface.screen_to_map(MapPoint(float(screen_position[0]), float(screen_position[1])))
        hit = self.game_map.hit_test(point)
        if hit.node_id is None or not self.game_map.world.selection.selected:
            return None
        return self.game_map.move_selected(hit.node_id, self.speed)
