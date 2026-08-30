from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any


class ProjectDocument:
    """Mutable, transaction-friendly representation of a data-driven project."""

    def __init__(self, root: str | Path, *, data: dict[str, Any] | None = None):
        self.root = Path(root).resolve()
        self.data: dict[str, Any] = deepcopy(data) if data is not None else self._load()
        self._snapshot: dict[str, Any] | None = None

    def _load(self) -> dict[str, Any]:
        path = self.root / "project.json"
        if not path.is_file():
            return {"name": self.root.name or "New Project", "version": "1.0", "map_path": "map.json", "start_scene": "map"}
        return json.loads(path.read_text(encoding="utf-8"))

    def begin(self) -> "ProjectDocument":
        if self._snapshot is not None:
            raise RuntimeError("Document transaction already active")
        self._snapshot = deepcopy(self.data)
        return self

    def commit(self) -> None:
        self._snapshot = None

    def rollback(self) -> None:
        if self._snapshot is None:
            raise RuntimeError("No active document transaction")
        self.data = self._snapshot
        self._snapshot = None

    def save(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        manifest = {key: self.data[key] for key in ("name", "version", "map_path", "start_scene") if key in self.data}
        (self.root / "project.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        map_data = self.data.get("map")
        if isinstance(map_data, dict):
            map_path = self.root / str(self.data.get("map_path", "map.json"))
            map_path.parent.mkdir(parents=True, exist_ok=True)
            (map_path).write_text(json.dumps(map_data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def manifest(self) -> dict[str, Any]:
        return {key: self.data.get(key) for key in ("name", "version", "map_path", "start_scene")}

    def ensure_map(self) -> dict[str, Any]:
        map_data = self.data.setdefault("map", {})
        if not isinstance(map_data, dict):
            raise ValueError("Project map must be an object")
        map_data.setdefault("width", 1200)
        map_data.setdefault("height", 700)
        map_data.setdefault("nodes", [])
        map_data.setdefault("connections", [])
        map_data.setdefault("entities", [])
        return map_data

    @staticmethod
    def _find_by_id(items: list[dict[str, Any]], item_id: str) -> dict[str, Any] | None:
        return next((item for item in items if item.get("id") == item_id), None)

    def add_node(self, node_id: str, x: float, y: float, *, label: str = "", metadata: dict[str, Any] | None = None) -> dict[str, Any]:
        nodes = self.ensure_map()["nodes"]
        if self._find_by_id(nodes, node_id):
            raise ValueError(f"Duplicate node: {node_id}")
        node = {"id": node_id, "x": float(x), "y": float(y), "label": label}
        if metadata: node["metadata"] = deepcopy(metadata)
        nodes.append(node)
        return node

    def add_connection(self, source: str, target: str, *, cost: float = 1.0, blocked: bool = False, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
        map_data = self.ensure_map()
        node_ids = {item["id"] for item in map_data["nodes"]}
        if source not in node_ids or target not in node_ids:
            raise ValueError(f"Unknown node in connection: {source} -> {target}")
        connection = {"source": source, "target": target, "cost": float(cost), "blocked": bool(blocked)}
        if metadata: connection["metadata"] = deepcopy(metadata)
        map_data["connections"].append(connection)
        return connection

    def add_entity(self, entity_id: str, node_id: str, *, components: dict[str, Any] | None = None) -> dict[str, Any]:
        map_data = self.ensure_map()
        node_ids = {item["id"] for item in map_data["nodes"]}
        if node_id not in node_ids:
            raise ValueError(f"Unknown node for entity: {node_id}")
        if self._find_by_id(map_data["entities"], entity_id):
            raise ValueError(f"Duplicate entity: {entity_id}")
        entity = {"id": entity_id, "node_id": node_id, "components": deepcopy(components or {})}
        map_data["entities"].append(entity)
        return entity

    def inspect(self) -> dict[str, Any]:
        map_data = self.data.get("map")
        return {
            "manifest": self.manifest(),
            "map": {
                "exists": isinstance(map_data, dict),
                "nodes": len(map_data.get("nodes", [])) if isinstance(map_data, dict) else 0,
                "connections": len(map_data.get("connections", [])) if isinstance(map_data, dict) else 0,
                "entities": len(map_data.get("entities", [])) if isinstance(map_data, dict) else 0,
            },
        }
