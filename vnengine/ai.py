from __future__ import annotations

from pathlib import Path
from typing import Any
from .ai_schema import command_schema as build_command_schema


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
                "running": bool(getattr(self.runtime, "running", getattr(getattr(self.runtime, "state", None), "running", False))),
                "scene": getattr(self.runtime, "scene_id", None),
                "scene_stack": list(self.runtime.stack.ids()) if hasattr(getattr(self.runtime, "stack", None), "ids") else [],
            },
            "capabilities": ["inspect", "validate", "scenes", "state", "commands", "save_load", "systems", "events"],
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
        if target == "systems":
            planner = getattr(self.runtime, "system_plan", None)
            return planner() if callable(planner) else {"order": [], "systems": []}
        raise ValueError(f"Unknown inspection target: {target}")

    def inspect_scene(self, scene_id: str | None = None) -> dict[str, Any]:
        active_id = getattr(self.runtime, "scene_id", None)
        scene = getattr(self.runtime, "scene", None) if scene_id is None or scene_id == active_id else None
        if scene is None: return {"id": scene_id, "active": False}
        methods = [name for name in ("enter", "exit", "pause", "resume", "update", "handle_input", "render", "serialize", "deserialize") if callable(getattr(scene, name, None))]
        return {"id": active_id, "active": True, "type": type(scene).__name__, "methods": methods}

    def inspect_map(self) -> dict[str, Any]:
        world = getattr(self.runtime, "world", None)
        definition = getattr(world, "definition", None)
        nested_world = getattr(world, "world", None)
        if definition is None and nested_world is not None:
            world = nested_world
            definition = getattr(world, "definition", None)
        if definition is None: return {"active": False}
        entities = [getattr(entity, "id", None) for entity in world.entities.all()] if hasattr(getattr(world, "entities", None), "all") else []
        return {"active": True, "width": definition.width, "height": definition.height, "nodes": [node.id for node in definition.nodes], "connections": len(definition.connections), "areas": len(definition.areas), "layers": len(definition.layers), "entities": entities}

    def validate(self) -> dict[str, Any]:
        errors: list[dict[str, Any]] = []
        warnings: list[dict[str, Any]] = []
        root = Path(self.runtime.project.root)
        manifest_path = root / "project.json"
        if not manifest_path.is_file(): errors.append({"code": "missing_manifest", "path": "project.json", "message": "Project manifest is missing."})
        manifest = self.runtime.project.manifest
        map_path = root / manifest.map_path
        if not map_path.is_file(): errors.append({"code": "missing_map", "path": str(map_path.relative_to(root)), "message": "Configured map file is missing."})
        start = manifest.start_scene
        if hasattr(self.runtime, "scenes") and not self.runtime.scenes.has(start): errors.append({"code": "unknown_start_scene", "path": "project.json", "message": f"Start scene is not registered: {start}"})
        planner = getattr(self.runtime, "system_plan", None)
        if callable(planner):
            try:
                plan = planner()
                for system in plan.get("systems", []):
                    if any(not item for item in system.get("requires", [])):
                        errors.append({"code": "invalid_system_requirement", "path": f"systems.json.{system.get('name')}", "message": "System has an empty component requirement."})
            except ValueError as exc:
                errors.append({"code": "system_graph_invalid", "path": "systems.json", "message": str(exc)})
        return {"valid": not errors, "errors": errors, "warnings": warnings}

    def command_schema(self) -> dict[str, Any]:
        return build_command_schema()

    def call(self, command: str, **kwargs: Any) -> Any:
        runtime_commands = self.command_schema().get("runtime_commands", {})
        allowed = {"start": self.runtime.start, "stop": self.runtime.stop, "switch_scene": self.runtime.switch_scene, "push_scene": self.runtime.push_scene, "pop_scene": self.runtime.pop_scene}
        if command not in allowed: raise ValueError(f"Unsupported AI command: {command}")
        spec = runtime_commands.get(command)
        if spec is None: raise ValueError(f"Command is missing from schema: {command}")
        missing = [name for name in spec["required"] if name not in kwargs]
        if missing: raise ValueError(f"Missing required arguments for {command}: {', '.join(missing)}")
        unexpected = sorted(set(kwargs) - set(spec["required"]) - set(spec["optional"]))
        if unexpected: raise ValueError(f"Unexpected arguments: {', '.join(unexpected)}")
        return allowed[command](**kwargs)
