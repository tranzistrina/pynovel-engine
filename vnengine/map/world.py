from __future__ import annotations
from typing import Any
from .entities import EntityRegistry, MapEntity
from .movement import MovementController
from .model import MapDefinition, MapPoint
from .selection import SelectionModel


class MapWorld:
    """Runtime container joining map data, entities, selection and movement."""
    def __init__(self, definition: MapDefinition):
        self.definition = definition
        self.entities = EntityRegistry()
        self.selection = SelectionModel()
        self.movement = MovementController(definition)

    def add_entity(self, entity_id: str, node_id: str, *, components: dict[str, Any] | None = None, metadata: dict[str, Any] | None = None) -> MapEntity:
        position = self.definition.node(node_id).position
        entity = MapEntity(entity_id, position, node_id, components or {}, metadata or {})
        self.entities.add(entity)
        return entity

    def update(self, dt: float) -> None:
        self.movement.update(dt)
        for entity_id, motion in self.movement.active.items():
            entity = self.entities.get(entity_id)
            if entity is not None:
                entity.position = motion.position
                if motion.finished: entity.node_id = motion.route.nodes[-1]

    def serialize(self) -> dict[str, Any]:
        return {"entities": self.entities.serialize(), "selection": list(self.selection.selected)}

    def deserialize(self, payload: dict[str, Any]) -> None:
        self.entities.deserialize(payload.get("entities", {}))
        self.selection.set(payload.get("selection", []))
