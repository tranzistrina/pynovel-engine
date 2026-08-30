from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable

from .model import MapPoint


@dataclass(frozen=True, slots=True)
class EntityHandle:
    """Stable logical handle for an entity within a project runtime."""
    id: str


@dataclass(slots=True)
class MapEntity:
    id: str
    position: MapPoint
    node_id: str | None = None
    components: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def handle(self) -> EntityHandle:
        return EntityHandle(self.id)
    def has_component(self, name: str) -> bool:
        return str(name) in self.components
    def get_component(self, name: str, default: Any = None) -> Any:
        return self.components.get(str(name), default)
    def set_component(self, name: str, value: Any) -> Any:
        key = str(name)
        if not key: raise ValueError("component name must not be empty")
        self.components[key] = value
        return value
    def remove_component(self, name: str) -> Any:
        return self.components.pop(str(name), None)


class EntityRegistry:
    """Lightweight ECS-lite registry with deterministic component operations."""
    def __init__(self, *, component_registry: Any = None):
        self._entities: dict[str, MapEntity] = {}
        self.component_registry = component_registry

    def add(self, entity: MapEntity) -> EntityHandle:
        self._validate_id(entity.id)
        if entity.id in self._entities: raise ValueError(f"Entity already exists: {entity.id}")
        self._validate_components(entity.components)
        self._entities[entity.id] = entity
        return entity.handle
    def upsert(self, entity: MapEntity) -> EntityHandle:
        self._validate_id(entity.id); self._validate_components(entity.components); self._entities[entity.id] = entity; return entity.handle
    def remove(self, entity_id: str) -> MapEntity | None: return self._entities.pop(str(entity_id), None)
    def get(self, entity_id: str | EntityHandle) -> MapEntity | None:
        key = entity_id.id if isinstance(entity_id, EntityHandle) else str(entity_id); return self._entities.get(key)
    def require(self, entity_id: str | EntityHandle) -> MapEntity:
        entity = self.get(entity_id)
        if entity is None:
            key = entity_id.id if isinstance(entity_id, EntityHandle) else str(entity_id); raise KeyError(f"Unknown entity: {key}")
        return entity
    def handle(self, entity_id: str) -> EntityHandle: return self.require(entity_id).handle
    def all(self) -> tuple[MapEntity, ...]: return tuple(self._entities.values())
    def ids(self) -> tuple[str, ...]: return tuple(self._entities)
    def query(self, *, component: str | None = None, node_id: str | None = None) -> tuple[MapEntity, ...]:
        result: Iterable[MapEntity] = self._entities.values()
        if component is not None: result = (entity for entity in result if str(component) in entity.components)
        if node_id is not None: result = (entity for entity in result if entity.node_id == str(node_id))
        return tuple(result)
    def at_node(self, node_id: str) -> tuple[MapEntity, ...]: return self.query(node_id=node_id)
    def set_position(self, entity_id: str | EntityHandle, position: MapPoint, node_id: str | None = None) -> None:
        entity = self.require(entity_id); entity.position = position
        if node_id is not None: entity.node_id = node_id
    def set_component(self, entity_id: str | EntityHandle, name: str, value: Any) -> Any:
        entity = self.require(entity_id); result = entity.set_component(name, value); self._validate_components(entity.components); return result
    def get_component(self, entity_id: str | EntityHandle, name: str, default: Any = None) -> Any: return self.require(entity_id).get_component(name, default)
    def remove_component(self, entity_id: str | EntityHandle, name: str) -> Any: return self.require(entity_id).remove_component(name)
    def apply_components(self, entity_id: str | EntityHandle, components: dict[str, Any], *, replace: bool = False) -> None:
        entity = self.require(entity_id); original = dict(entity.components); entity.components = dict(components) if replace else {**entity.components, **components}
        try: self._validate_components(entity.components)
        except Exception: entity.components = original; raise
    def batch_set_component(self, updates: Iterable[tuple[str, str, Any]]) -> None:
        original = {entity_id: dict(self.require(entity_id).components) for entity_id, _, _ in updates}
        try:
            for entity_id, name, value in updates: self.set_component(entity_id, name, value)
        except Exception:
            for entity_id, components in original.items(): self.require(entity_id).components = components
            raise
    def validate(self) -> dict[str, list[str]]:
        return {entity.id: self._component_errors(entity.components) for entity in self.all() if self._component_errors(entity.components)}
    def serialize(self) -> dict[str, Any]:
        return {entity_id: {"position": [entity.position.x, entity.position.y], "node_id": entity.node_id, "components": dict(sorted(entity.components.items())), "metadata": dict(sorted(entity.metadata.items()))} for entity_id, entity in sorted(self._entities.items())}
    def deserialize(self, payload: dict[str, Any]) -> None:
        if not isinstance(payload, dict): raise ValueError("Entity payload must be an object")
        self._entities.clear()
        for entity_id, data in sorted(payload.items()):
            if not isinstance(data, dict): raise ValueError(f"Entity definition must be an object: {entity_id}")
            pos = data.get("position", [0, 0])
            if not isinstance(pos, (list, tuple)) or len(pos) != 2: raise ValueError(f"Invalid entity position: {entity_id}")
            self.add(MapEntity(str(entity_id), MapPoint(float(pos[0]), float(pos[1])), data.get("node_id"), dict(data.get("components", {})), dict(data.get("metadata", {}))))
    def _component_errors(self, components: dict[str, Any]) -> list[str]:
        if self.component_registry is None: return []
        return list(self.component_registry.validate(components))
    def _validate_components(self, components: dict[str, Any]) -> None:
        errors = self._component_errors(components)
        if errors: raise ValueError("; ".join(errors))
    @staticmethod
    def _validate_id(entity_id: str) -> None:
        if not str(entity_id).strip(): raise ValueError("Entity id must not be empty")
