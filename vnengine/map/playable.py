from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from .input import MapInputAdapter
from .model import MapDefinition, MapPoint
from .route_builder import RouteBuilder
from .world import MapWorld
from .world_controller import MapWorldController


@dataclass(frozen=True, slots=True)
class MapSelectionHit:
    entity_id: str | None
    node_id: str | None


class PlayableMap:
    """Engine-side playable map coordinator, independent of a specific game."""
    def __init__(self, definition: MapDefinition, *, emit=None):
        self.world = MapWorld(definition, emit)
        self.routes = RouteBuilder(definition)
        self.controller = MapWorldController(self.world, self.routes, emit)

    def add_entity(self, entity_id: str, node_id: str, **kwargs: Any):
        return self.world.add_entity(entity_id, node_id, **kwargs)

    def move_selected(self, target_node: str, speed: float = 100.0):
        return self.controller.move_selected(target_node, speed)

    def update(self, dt: float) -> None:
        self.controller.update(dt)

    def serialize(self) -> dict[str, Any]:
        return self.world.serialize()

    def deserialize(self, payload: dict[str, Any]) -> None:
        self.world.deserialize(payload)
