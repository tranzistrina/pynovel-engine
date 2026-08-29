from __future__ import annotations
from typing import Any
from .entities import EntityRegistry, MapEntity
from .movement import MovementController
from .model import MapDefinition
from .selection import SelectionModel


class MapWorld:
    """Runtime container joining map data, entities, selection and movement."""
    def __init__(self, definition: MapDefinition, emit=None):
        self.definition = definition; self.entities = EntityRegistry(); self.selection = SelectionModel(); self.movement = MovementController(definition, emit)

    def add_entity(self, entity_id: str, node_id: str, *, components: dict[str, Any] | None = None, metadata: dict[str, Any] | None = None) -> MapEntity:
        position = self.definition.node(node_id).position; entity = MapEntity(entity_id, position, node_id, components or {}, metadata or {})
        self.entities.add(entity); self.selection.register(entity_id); return entity

    def remove_entity(self, entity_id: str) -> MapEntity | None:
        self.selection.unregister(entity_id); self.movement.cancel(entity_id); return self.entities.remove(entity_id)

    def update(self, dt: float) -> None:
        self.movement.update(dt)
        for entity_id, motion in self.movement.active.items():
            entity = self.entities.get(entity_id)
            if entity is not None:
                entity.position = motion.position
                if motion.finished: entity.node_id = motion.route.nodes[-1]

    def serialize(self) -> dict[str, Any]:
        movements = {entity_id: {"route": list(m.route.nodes), "position": [m.position.x, m.position.y], "segment": m.segment, "progress": m.progress, "speed": m.speed, "paused": m.paused, "cost": m.route.cost} for entity_id, m in self.movement.active.items()}
        return {"entities": self.entities.serialize(), "selection": list(self.selection.selected), "movements": movements}

    def deserialize(self, payload: dict[str, Any]) -> None:
        self.entities.deserialize(payload.get("entities", {})); self.selection.clear()
        for entity in self.entities.all(): self.selection.register(entity.id)
        for entity_id in payload.get("selection", []):
            if self.entities.get(entity_id) is not None: self.selection.select(entity_id, additive=True)
        self.movement.restore(payload.get("movements", {}))
