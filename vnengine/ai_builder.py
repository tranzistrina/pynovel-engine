from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class AIProjectBuilder:
    """Deterministic, high-level project authoring API for coding agents."""

    def __init__(self, root: str | Path):
        self.root = Path(root).resolve()
        self.manifest_path = self.root / "project.json"
        self.map_path = self.root / "map.json"

    def create_project(self, name: str, *, version: str = "1.0", map_path: str = "map.json", start_scene: str = "map") -> dict[str, Any]:
        self.root.mkdir(parents=True, exist_ok=True)
        manifest = {"name": name, "version": version, "map_path": map_path, "start_scene": start_scene}
        self._write_json(self.manifest_path, manifest)
        return manifest

    def create_map(self, *, width: float, height: float, background: str | None = None) -> dict[str, Any]:
        payload = {"width": width, "height": height, "nodes": [], "connections": [], "entities": []}
        if background is not None: payload["background"] = background
        self._write_json(self.map_path, payload)
        return payload

    def add_node(self, node_id: str, x: float, y: float, *, label: str = "", metadata: dict[str, Any] | None = None) -> dict[str, Any]:
        data = self._read_map(); self._ensure_unique_id(data["nodes"], node_id, "node")
        node = {"id": node_id, "x": x, "y": y, "label": label}
        if metadata: node["metadata"] = dict(metadata)
        data["nodes"].append(node); self._write_json(self.map_path, data); return node

    def add_connection(self, source: str, target: str, *, cost: float = 1.0, blocked: bool = False, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
        data = self._read_map(); node_ids = {item["id"] for item in data["nodes"]}
        if source not in node_ids or target not in node_ids: raise ValueError(f"Unknown node in connection: {source} -> {target}")
        connection = {"source": source, "target": target, "cost": cost, "blocked": blocked}
        if metadata: connection["metadata"] = dict(metadata)
        data["connections"].append(connection); self._write_json(self.map_path, data); return connection

    def add_entity(self, entity_id: str, node_id: str, *, components: dict[str, Any] | None = None) -> dict[str, Any]:
        data = self._read_map(); self._ensure_unique_id(data["entities"], entity_id, "entity")
        if node_id not in {item["id"] for item in data["nodes"]}: raise ValueError(f"Unknown node for entity: {node_id}")
        entity = {"id": entity_id, "node_id": node_id, "components": dict(components or {})}
        data["entities"].append(entity); self._write_json(self.map_path, data); return entity

    def inspect(self) -> dict[str, Any]:
        manifest = self._read_json(self.manifest_path) if self.manifest_path.is_file() else None
        map_data = self._read_json(self.map_path) if self.map_path.is_file() else None
        return {
            "root": str(self.root),
            "manifest": manifest,
            "map": {
                "exists": map_data is not None,
                "nodes": len(map_data.get("nodes", [])) if map_data else 0,
                "connections": len(map_data.get("connections", [])) if map_data else 0,
                "entities": len(map_data.get("entities", [])) if map_data else 0,
            },
        }

    def _read_map(self) -> dict[str, Any]:
        if not self.map_path.is_file(): raise FileNotFoundError(f"Map file does not exist: {self.map_path}")
        return self._read_json(self.map_path)

    @staticmethod
    def _ensure_unique_id(items: list[dict[str, Any]], item_id: str, kind: str) -> None:
        if any(str(item.get("id")) == item_id for item in items): raise ValueError(f"Duplicate {kind} id: {item_id}")

    @staticmethod
    def _read_json(path: Path) -> dict[str, Any]:
        with path.open("r", encoding="utf-8") as handle: return json.load(handle)

    @staticmethod
    def _write_json(path: Path, payload: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
