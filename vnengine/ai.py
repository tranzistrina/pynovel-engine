from __future__ import annotations

from pathlib import Path
from typing import Any


class AIProjectAPI:
    """Small, deterministic facade intended for coding agents."""
    API_VERSION = 2

    def __init__(self, runtime: Any):
        self.runtime = runtime

    def describe(self) -> dict[str, Any]:
        return {
            "engine": "pynovel-engine",
            "api_version": self.API_VERSION,
            "project": self.project(),
            "runtime": {
                "running": bool(getattr(self.runtime, "running", False)),
                "scene": self.runtime.scene_id,
                "scene_stack": list(self.runtime.stack.ids()),
            },
            "capabilities": ["inspect", "validate", "scenes", "state", "commands", "save_load"],
        }

    def project(self) -> dict[str, Any]:
        manifest = self.runtime.project.manifest
        return {
            "root": str(self.runtime.project.root),
            "name": manifest.name,
            "version": manifest.version,
            "map_path": manifest.map_path,
            "start_scene": manifest.start_scene,
        }

    def scenes(self) -> list[str]:
        return sorted(self.runtime.scenes.ids())

    def state(self) -> dict[str, Any]:
        return self.runtime.save_state()

    def inspect(self, target: str = "project") -> dict[str, Any]:
        if target == "project": return self.project()
        if target == "runtime": return self.describe()["runtime"]
        if target == "scene": return self.inspect_scene()
        if target == "map": return self.inspect_map()
        raise ValueError(f"Unknown inspection target: {target}")

    def inspect_scene(self, scene_id: str | None = None) -> dict[str, Any]:
        scene = self.runtime.scene if scene_id is None or scene_id == self.runtime.scene_id else None
        if scene is None: return {"id": scene_id, "active": False}
        methods = [name for name in ("enter", "exit", "pause", "resume", "update", "handle_input", "render", "serialize", "deserialize") if callable(getattr(scene, name, None))]
        return {"id": self.runtime.scene_id, "active": True, "type": type(scene).__name__, "methods": methods}

    def inspect_map(self) -> dict[str, Any]:
        world = getattr(self.runtime, "world", None)
        definition = getattr(world, "definition", None)
        if definition is None: return {"active": False}
        return {
            "active": True,
            "width": definition.width,
            "height": definition.height,
            "nodes": [node.id for node in definition.nodes],
            "connections": len(definition.connections),
            "areas": len(definition.areas),
            "layers": len(definition.layers),
            "entities": [getattr(entity, "id", None) for entity in world.entities.all()] if hasattr(world, "entities") else [],
        }

    def validate(self) -> dict[str, Any]:
        errors: list[dict[str, Any]] = []
        warnings: list[dict[str, Any]] = []
        root = Path(self.runtime.project.root)
        if not (root / "project.json").is_file(): errors.append({"code": "missing_manifest", "path": "project.json", "message": "Project manifest is missing."})
        map_path = root / self.runtime.project.manifest.map_path
        if not map_path.is_file(): errors.append({"code": "missing_map", "path": str(map_path.relative_to(root)), "message": "Configured map file is missing."})
        start = self.runtime.project.manifest.start_scene
        if not self.runtime.scenes.has(start): errors.append({"code": "unknown_start_scene", "path": "project.json", "message": f"Start scene is not registered: {start}"})
        if not errors and self.runtime.world is not None:
            definition = getattr(self.runtime.world, "definition", None)
            if definition is not None:
                node_ids = {node.id for node in definition.nodes}
                for connection in definition.connections:
                    if connection.source not in node_ids or connection.target not in node_ids:
                        errors.append({"code": "invalid_connection", "path": str(map_path.relative_to(root)), "message": f"Connection references an unknown node: {connection.source} -> {connection.target}."})
        return {"valid": not errors, "errors": errors, "warnings": warnings}

    def command_schema(self) -> dict[str, Any]:
        return {
            "api_version": self.API_VERSION,
            "commands": {
                "start": {"description": "Start the project runtime.", "required": []},
                "stop": {"description": "Stop the project runtime.", "required": []},
                "switch_scene": {"description": "Replace the scene stack with one scene.", "required": ["scene_id"]},
                "push_scene": {"description": "Push a scene over the current scene.", "required": ["scene_id"]},
                "pop_scene": {"description": "Pop the current overlay scene.", "required": []},
            },
        }

    def call(self, command: str, **kwargs: Any) -> Any:
        allowed = {
            "start": self.runtime.start,
            "stop": self.runtime.stop,
            "switch_scene": self.runtime.switch_scene,
            "push_scene": self.runtime.push_scene,
            "pop_scene": self.runtime.pop_scene,
        }
        if command not in allowed: raise ValueError(f"Unsupported AI command: {command}")
        required = next((item["required"] for name, item in self.command_schema()["commands"].items() if name == command), [])
        missing = [name for name in required if name not in kwargs]
        if missing: raise ValueError(f"Missing required arguments for {command}: {', '.join(missing)}")
        return allowed[command](**kwargs)
