from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .model import MapDefinition, MapPoint
from .route_builder import RouteBuilder
from .world import MapWorld
from .world_controller import MapWorldController


@dataclass(frozen=True, slots=True)
class MapSelectionHit:
    entity_id: str | None = None
    node_id: str | None = None


class PlayableMap:
    """Engine-side playable map coordinator, independent of a specific game."""

    def __init__(self, definition: MapDefinition, *, emit=None, hit_radius: float = 24.0):
        self.world = MapWorld(definition, emit)
        self.routes = RouteBuilder(definition, entity_resolver=self._entity_node)
        self.controller = MapWorldController(self.world, self.routes, emit)
        self.hit_radius = float(hit_radius)

    def _entity_node(self, entity_id: str) -> str | None:
        entity = self.world.entities.get(entity_id)
        return None if entity is None else entity.node_id

    def add_entity(self, entity_id: str, node_id: str, **kwargs: Any):
        return self.world.add_entity(entity_id, node_id, **kwargs)

    def hit_test(self, map_position: MapPoint) -> MapSelectionHit:
        radius2 = self.hit_radius * self.hit_radius
        nearest_entity: tuple[float, str] | None = None
        for entity in self.world.entities.all():
            dx = entity.position.x - map_position.x; dy = entity.position.y - map_position.y; distance2 = dx * dx + dy * dy
            if distance2 <= radius2 and (nearest_entity is None or distance2 < nearest_entity[0]): nearest_entity = (distance2, entity.id)
        if nearest_entity is not None: return MapSelectionHit(entity_id=nearest_entity[1])
        nearest_node: tuple[float, str] | None = None
        for node in self.world.definition.nodes:
            dx = node.position.x - map_position.x; dy = node.position.y - map_position.y; distance2 = dx * dx + dy * dy
            if distance2 <= radius2 and (nearest_node is None or distance2 < nearest_node[0]): nearest_node = (distance2, node.id)
        return MapSelectionHit(node_id=nearest_node[1]) if nearest_node is not None else MapSelectionHit()

    def select_at(self, map_position: MapPoint, additive: bool = False) -> MapSelectionHit:
        hit = self.hit_test(map_position)
        if hit.entity_id is not None: self.world.selection.select(hit.entity_id, additive=additive)
        return hit

    def move_selected(self, target_node: str, speed: float = 100.0): return self.controller.move_selected(target_node, speed)
    def update(self, dt: float) -> None: self.controller.update(dt)
    def serialize(self) -> dict[str, Any]: return self.world.serialize()
    def deserialize(self, payload: dict[str, Any]) -> None: self.world.deserialize(payload)
