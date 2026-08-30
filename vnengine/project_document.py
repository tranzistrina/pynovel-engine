from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any


class ProjectDocument:
    """Mutable, transaction-friendly representation of a complete game project."""
    def __init__(self, root: str | Path, *, data: dict[str, Any] | None = None):
        self.root = Path(root).resolve(); self.data = deepcopy(data) if data is not None else self._load(); self._snapshot: dict[str, Any] | None = None

    def _load(self) -> dict[str, Any]:
        manifest_path = self.root / "project.json"
        if not manifest_path.is_file(): return {"name": self.root.name or "New Project", "version": "1.0", "map_path": "map.json", "start_scene": "map", "variables": {}}
        data = json.loads(manifest_path.read_text(encoding="utf-8")); map_path = self.root / str(data.get("map_path", "map.json"))
        if map_path.is_file(): data["map"] = json.loads(map_path.read_text(encoding="utf-8"))
        for key, filename in (("scenes", "scenes.json"), ("resources", "resources.json")):
            path = self.root / filename
            if path.is_file(): data[key] = json.loads(path.read_text(encoding="utf-8"))
        return data

    def begin(self) -> "ProjectDocument":
        if self._snapshot is not None: raise RuntimeError("Document transaction already active")
        self._snapshot = deepcopy(self.data); return self
    def commit(self) -> None: self._snapshot = None
    def rollback(self) -> None:
        if self._snapshot is None: raise RuntimeError("No active document transaction")
        self.data = self._snapshot; self._snapshot = None

    def save(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        manifest = {key: self.data[key] for key in ("name", "version", "map_path", "start_scene", "variables") if key in self.data}
        (self.root / "project.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        for key, filename in (("map", self.data.get("map_path", "map.json")), ("scenes", "scenes.json"), ("resources", "resources.json")):
            payload = self.data.get(key)
            if isinstance(payload, dict):
                path = self.root / str(filename); path.parent.mkdir(parents=True, exist_ok=True); path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def manifest(self) -> dict[str, Any]: return {key: self.data.get(key) for key in ("name", "version", "map_path", "start_scene", "variables")}
    def ensure_variables(self) -> dict[str, Any]:
        value = self.data.setdefault("variables", {})
        if not isinstance(value, dict): raise ValueError("Project variables must be an object")
        return value
    def set_variable(self, key: str, value: Any) -> Any:
        if not key: raise ValueError("Variable name cannot be empty")
        self.ensure_variables()[str(key)] = deepcopy(value); return value
    def ensure_map(self) -> dict[str, Any]:
        data = self.data.setdefault("map", {})
        if not isinstance(data, dict): raise ValueError("Project map must be an object")
        data.setdefault("width", 1200); data.setdefault("height", 700); data.setdefault("nodes", []); data.setdefault("connections", []); data.setdefault("entities", []); return data
    def ensure_scenes(self) -> dict[str, dict[str, Any]]:
        data = self.data.setdefault("scenes", {})
        if not isinstance(data, dict): raise ValueError("Project scenes must be an object")
        return data
    def ensure_resources(self) -> dict[str, dict[str, Any]]:
        data = self.data.setdefault("resources", {})
        if not isinstance(data, dict): raise ValueError("Project resources must be an object")
        return data
    def add_resource(self, resource_id: str, path: str, resource_type: str, *, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
        resources = self.ensure_resources()
        if resource_id in resources: raise ValueError(f"Duplicate resource: {resource_id}")
        item = {"id": str(resource_id), "path": str(path).replace("\\", "/"), "type": str(resource_type)}
        if metadata: item["metadata"] = deepcopy(metadata)
        resources[item["id"]] = item; return item
    def remove_resource(self, resource_id: str) -> dict[str, Any]:
        try: return self.ensure_resources().pop(resource_id)
        except KeyError as exc: raise ValueError(f"Unknown resource: {resource_id}") from exc
    def add_scene(self, scene_id: str, *, background: str | None = None) -> dict[str, Any]:
        scenes = self.ensure_scenes()
        if scene_id in scenes: raise ValueError(f"Duplicate scene: {scene_id}")
        scene = {"id": scene_id, "actions": []}
        if background is not None: scene["background"] = background
        scenes[scene_id] = scene; return scene
    def remove_scene(self, scene_id: str) -> dict[str, Any]:
        scenes = self.ensure_scenes()
        if scene_id not in scenes: raise ValueError(f"Unknown scene: {scene_id}")
        if str(self.data.get("start_scene")) == scene_id: raise ValueError("Start scene cannot be removed")
        return scenes.pop(scene_id)
    def add_scene_action(self, scene_id: str, action: dict[str, Any]) -> dict[str, Any]:
        scene = self.ensure_scenes().get(scene_id)
        if scene is None: raise ValueError(f"Unknown scene: {scene_id}")
        scene.setdefault("actions", []).append(deepcopy(action)); return action
    @staticmethod
    def _find_by_id(items: list[dict[str, Any]], item_id: str) -> dict[str, Any] | None: return next((item for item in items if item.get("id") == item_id), None)
    def add_node(self, node_id: str, x: float, y: float, *, label: str = "", metadata: dict[str, Any] | None = None) -> dict[str, Any]:
        nodes = self.ensure_map()["nodes"]
        if self._find_by_id(nodes, node_id): raise ValueError(f"Duplicate node: {node_id}")
        node = {"id": node_id, "x": float(x), "y": float(y), "label": label}
        if metadata: node["metadata"] = deepcopy(metadata)
        nodes.append(node); return node
    def add_connection(self, source: str, target: str, *, cost: float = 1.0, blocked: bool = False, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
        data = self.ensure_map(); ids = {item["id"] for item in data["nodes"]}
        if source not in ids or target not in ids: raise ValueError(f"Unknown node in connection: {source} -> {target}")
        connection = {"source": source, "target": target, "cost": float(cost), "blocked": bool(blocked)}
        if metadata: connection["metadata"] = deepcopy(metadata)
        data["connections"].append(connection); return connection
    def add_entity(self, entity_id: str, node_id: str, *, components: dict[str, Any] | None = None) -> dict[str, Any]:
        data = self.ensure_map(); ids = {item["id"] for item in data["nodes"]}
        if node_id not in ids: raise ValueError(f"Unknown node for entity: {node_id}")
        if self._find_by_id(data["entities"], entity_id): raise ValueError(f"Duplicate entity: {entity_id}")
        entity = {"id": entity_id, "node_id": node_id, "components": deepcopy(components or {})}; data["entities"].append(entity); return entity
    def inspect(self) -> dict[str, Any]:
        data = self.data; m, s, r, v = data.get("map"), data.get("scenes"), data.get("resources"), data.get("variables")
        return {"manifest": self.manifest(), "variables": len(v) if isinstance(v, dict) else 0, "scenes": len(s) if isinstance(s, dict) else 0, "resources": len(r) if isinstance(r, dict) else 0, "map": {"exists": isinstance(m, dict), "nodes": len(m.get("nodes", [])) if isinstance(m, dict) else 0, "connections": len(m.get("connections", [])) if isinstance(m, dict) else 0, "entities": len(m.get("entities", [])) if isinstance(m, dict) else 0}}
