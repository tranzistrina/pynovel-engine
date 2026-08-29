from __future__ import annotations
from .entities import EntityRegistry
from .movement import MovementController


class EntityMovementBridge:
    """Keeps registry positions synchronized with active map movement."""
    def __init__(self, entities: EntityRegistry, movement: MovementController):
        self.entities = entities
        self.movement = movement

    def update(self, dt: float) -> None:
        self.movement.update(dt)
        for entity_id, active in self.movement.active.items():
            entity = self.entities.get(entity_id)
            if entity is not None:
                entity.position = active.position
                if active.finished:
                    entity.node_id = active.route.nodes[-1]
