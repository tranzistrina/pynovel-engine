from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from .project_document import ProjectDocument


class AIProjectBuilder:
    """High-level, transactional project authoring API for coding agents."""

    def __init__(self, root: str | Path, *, document: ProjectDocument | None = None):
        self.document = document or ProjectDocument(root)
        self.root = self.document.root

    @property
    def manifest_path(self) -> Path: return self.root / "project.json"
    @property
    def map_path(self) -> Path: return self.root / str(self.document.data.get("map_path", "map.json"))

    def create_project(self, name: str, *, version: str = "1.0", map_path: str = "map.json", start_scene: str = "map") -> dict[str, Any]:
        self.document.data.update({"name": str(name), "version": str(version), "map_path": str(map_path), "start_scene": str(start_scene)})
        return self.document.manifest()

    def create_map(self, *, width: float, height: float, background: str | None = None) -> dict[str, Any]:
        payload = self.document.ensure_map(); payload.update({"width": float(width), "height": float(height), "nodes": [], "connections": [], "entities": []})
        if background is not None: payload["background"] = background
        return payload

    def add_scene(self, scene_id: str, *, background: str | None = None) -> dict[str, Any]:
        return self.document.add_scene(scene_id, background=background)

    def add_scene_action(self, scene_id: str, action_type: str, **data: Any) -> dict[str, Any]:
        return self.document.add_scene_action(scene_id, {"type": action_type, **data})

    def add_node(self, node_id: str, x: float, y: float, *, label: str = "", metadata: dict[str, Any] | None = None) -> dict[str, Any]:
        return self.document.add_node(node_id, x, y, label=label, metadata=metadata)

    def add_connection(self, source: str, target: str, *, cost: float = 1.0, blocked: bool = False, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
        return self.document.add_connection(source, target, cost=cost, blocked=blocked, metadata=metadata)

    def add_entity(self, entity_id: str, node_id: str, *, components: dict[str, Any] | None = None) -> dict[str, Any]:
        return self.document.add_entity(entity_id, node_id, components=components)

    def set_map_property(self, key: str, value: Any) -> Any:
        if key in {"nodes", "connections", "entities"}: raise ValueError(f"Map collection cannot be replaced: {key}")
        self.document.ensure_map()[str(key)] = value; return value

    def set_entity_property(self, entity_id: str, key: str, value: Any) -> Any:
        entity = self.document._find_by_id(self.document.ensure_map()["entities"], entity_id)
        if entity is None: raise ValueError(f"Unknown entity: {entity_id}")
        if key == "id": raise ValueError("Entity id cannot be changed")
        entity[str(key)] = value; return value

    def remove_node(self, node_id: str) -> dict[str, Any]:
        payload = self.document.ensure_map(); node = self.document._find_by_id(payload["nodes"], node_id)
        if node is None: raise ValueError(f"Unknown node: {node_id}")
        if any(c.get("source") == node_id or c.get("target") == node_id for c in payload["connections"]): raise ValueError(f"Cannot remove node with connections: {node_id}")
        if any(e.get("node_id") == node_id for e in payload["entities"]): raise ValueError(f"Cannot remove node with entities: {node_id}")
        payload["nodes"].remove(node); return node

    def remove_entity(self, entity_id: str) -> dict[str, Any]:
        entities = self.document.ensure_map()["entities"]; entity = self.document._find_by_id(entities, entity_id)
        if entity is None: raise ValueError(f"Unknown entity: {entity_id}")
        entities.remove(entity); return entity

    def transaction(self) -> ProjectDocument: return self.document.begin()
    def commit(self, *, save: bool = True) -> None:
        self.document.commit()
        if save: self.document.save()
    def rollback(self) -> None: self.document.rollback()

    def apply(self, operations: list[dict[str, Any]], *, save: bool = True) -> dict[str, Any]:
        self.document.begin()
        try: results = [self._dispatch(operation) for operation in operations]
        except Exception:
            self.document.rollback(); raise
        self.document.commit()
        if save: self.document.save()
        return {"applied": len(results), "results": results, "project": self.inspect()}

    def _dispatch(self, operation: dict[str, Any]) -> Any:
        payload = dict(operation); command = payload.pop("command", None)
        if not isinstance(command, str): raise ValueError("Operation requires a string 'command'")
        allowed: dict[str, Callable[..., Any]] = {
            "create_project": self.create_project, "create_map": self.create_map, "add_scene": self.add_scene,
            "add_scene_action": self.add_scene_action, "add_node": self.add_node, "add_connection": self.add_connection,
            "add_entity": self.add_entity, "set_map_property": self.set_map_property, "set_entity_property": self.set_entity_property,
            "remove_node": self.remove_node, "remove_entity": self.remove_entity,
        }
        handler = allowed.get(command)
        if handler is None: raise ValueError(f"Unsupported builder command: {command}")
        return handler(**payload)

    def inspect(self) -> dict[str, Any]: return {"root": str(self.root), **self.document.inspect()}
