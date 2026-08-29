from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
from .model import MapPoint


@dataclass(slots=True)
class MapEntity:
    id: str
    position: MapPoint
    node_id: str | None = None
    components: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


class EntityRegistry:
    """Lightweight engine-level registry. Gameplay components remain opaque."""
    def __init__(self):
        self._entities: dict[str, MapEntity] = {}

    def add(self, entity: MapEntity) -> None:
        if entity.id in self._entities: raise ValueError(f"Entity already exists: {entity.id}")
        self._entities[entity.id] = entity

    def upsert(self, entity: MapEntity) -> None: self._entities[entity.id] = entity
    def remove(self, entity_id: str) -> MapEntity | None: return self._entities.pop(entity_id, None)
    def get(self, entity_id: str) -> MapEntity | None: return self._entities.get(entity_id)
    def require(self, entity_id: str) -> MapEntity:
        entity = self.get(entity_id)
        if entity is None: raise KeyError(f"Unknown entity: {entity_id}")
        return entity
    def all(self) -> tuple[MapEntity, ...]: return tuple(self._entities.values())
    def at_node(self, node_id: str) -> tuple[MapEntity, ...]: return tuple(e for e in self._entities.values() if e.node_id == node_id)
    def set_position(self, entity_id: str, position: MapPoint, node_id: str | None = None) -> None:
        entity = self.require(entity_id); entity.position = position
        if node_id is not None: entity.node_id = node_id

    def serialize(self) -> dict[str, Any]:
        return {e.id: {"position": [e.position.x, e.position.y], "node_id": e.node_id, "components": e.components, "metadata": e.metadata} for e in self._entities.values()}

    def deserialize(self, payload: dict[str, Any]) -> None:
        self._entities.clear()
        for entity_id, data in payload.items():
            pos = data.get("position", [0, 0])
            self.add(MapEntity(str(entity_id), MapPoint(float(pos[0]), float(pos[1])), data.get("node_id"), dict(data.get("components", {})), dict(data.get("metadata", {}))))
