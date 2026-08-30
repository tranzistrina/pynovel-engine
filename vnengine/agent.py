from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .ai import AIProjectAPI
from .ai_builder import AIProjectBuilder
from .ai_schema import BUILDER_COMMANDS, command_schema


@dataclass(frozen=True, slots=True)
class Diagnostic:
    severity: str
    code: str
    message: str
    path: str | None = None
    suggestion: str | None = None

    def to_dict(self) -> dict[str, Any]:
        data = {"severity": self.severity, "code": self.code, "message": self.message}
        if self.path is not None: data["path"] = self.path
        if self.suggestion is not None: data["suggestion"] = self.suggestion
        return data


class AIAgentInterface:
    """Single stable API for AI agents to inspect, plan, mutate and diagnose projects."""
    API_VERSION = 4

    def __init__(self, root: str | Path, *, runtime: Any = None):
        self.root = Path(root).resolve(); self.builder = AIProjectBuilder(self.root)
        self.runtime = runtime; self.runtime_api = AIProjectAPI(runtime) if runtime is not None else None

    def capabilities(self) -> dict[str, Any]:
        return {"api_version": self.API_VERSION, "features": ["inspect", "plan", "dry_run", "apply", "validate", "diagnose", "transactions"], "commands": self.command_schema()}

    def inspect(self) -> dict[str, Any]:
        result = self.builder.inspect()
        if self.runtime_api is not None: result["runtime"] = self.runtime_api.describe()["runtime"]
        return result

    def plan(self, operations: list[dict[str, Any]]) -> dict[str, Any]:
        diagnostics: list[dict[str, Any]] = []
        specs = {spec.name: spec for spec in BUILDER_COMMANDS}
        for index, operation in enumerate(operations):
            location = f"operations[{index}]"
            if not isinstance(operation, dict):
                diagnostics.append(Diagnostic("error", "invalid_operation", "Operation must be an object.", location).to_dict()); continue
            command = operation.get("command"); spec = specs.get(command)
            if spec is None:
                diagnostics.append(Diagnostic("error", "unknown_command", f"Unsupported builder command: {command}", f"{location}.command").to_dict()); continue
            for name in spec.required:
                if name not in operation: diagnostics.append(Diagnostic("error", "missing_argument", f"Missing required argument: {name}", f"{location}.{name}").to_dict())
            allowed = set(spec.required) | set(spec.optional) | {"command"}
            for name in operation:
                if name not in allowed: diagnostics.append(Diagnostic("error", "unexpected_argument", f"Unexpected argument: {name}", f"{location}.{name}").to_dict())
        return {"valid": not diagnostics, "operations": len(operations), "diagnostics": diagnostics}

    def dry_run(self, operations: list[dict[str, Any]]) -> dict[str, Any]:
        plan = self.plan(operations); before = self.builder.document.inspect()
        if not plan["valid"]: return {"committed": False, "applied": 0, "before": before, "preview": before, "plan": plan, "diagnostics": plan["diagnostics"]}
        self.builder.document.begin()
        try:
            results = [self.builder._dispatch(op) for op in operations]; preview = self.builder.document.inspect()
        except Exception as exc:
            self.builder.document.rollback(); return {"committed": False, "applied": 0, "before": before, "preview": before, "plan": plan, "diagnostics": [self._exception_diagnostic(exc).to_dict()]}
        self.builder.document.rollback(); return {"committed": False, "applied": len(results), "before": before, "preview": preview, "plan": plan, "diagnostics": []}

    def apply(self, operations: list[dict[str, Any]], *, save: bool = True, validate: bool = True) -> dict[str, Any]:
        plan = self.plan(operations)
        if not plan["valid"]: return {"committed": False, "applied": 0, "plan": plan, "diagnostics": plan["diagnostics"]}
        try: result = self.builder.apply(operations, save=save)
        except Exception as exc: return {"committed": False, "applied": 0, "plan": plan, "diagnostics": [self._exception_diagnostic(exc).to_dict()]}
        validation = self.validate() if validate else {"valid": True, "errors": [], "warnings": []}
        result.update({"committed": True, "validation": validation, "diagnostics": validation["errors"] + validation["warnings"]}); return result

    def execute(self, operations: list[dict[str, Any]], *, dry_run: bool = False, save: bool = True, validate: bool = True) -> dict[str, Any]:
        return self.dry_run(operations) if dry_run else self.apply(operations, save=save, validate=validate)

    def validate(self) -> dict[str, Any]:
        errors: list[dict[str, Any]] = []; warnings: list[dict[str, Any]] = []; manifest_path = self.root / "project.json"
        if not manifest_path.is_file(): return {"valid": False, "errors": [Diagnostic("error", "missing_manifest", "Project manifest is missing.", "project.json", "Run create_project first.").to_dict()], "warnings": []}
        try: manifest = self._read_json(manifest_path)
        except Exception as exc: return {"valid": False, "errors": [Diagnostic("error", "invalid_manifest_json", str(exc), "project.json", "Fix the JSON syntax.").to_dict()], "warnings": []}
        for key in ("name", "version", "map_path", "start_scene"):
            if key not in manifest: errors.append(Diagnostic("error", "missing_manifest_field", f"Manifest field is missing: {key}", "project.json").to_dict())
        map_path = self.root / str(manifest.get("map_path", "map.json"))
        if not map_path.is_file(): errors.append(Diagnostic("error", "missing_map", "Configured map file is missing.", str(map_path.relative_to(self.root)), "Create a map or correct map_path.").to_dict())
        else: self._validate_map(map_path, errors, warnings)
        if self.runtime is not None:
            start = manifest.get("start_scene")
            if start and not self.runtime.scenes.has(start): errors.append(Diagnostic("error", "unknown_start_scene", f"Start scene is not registered: {start}", "project.json").to_dict())
        return {"valid": not errors, "errors": errors, "warnings": warnings}

    def diagnose(self) -> dict[str, Any]:
        validation = self.validate(); diagnostics = validation["errors"] + validation["warnings"]
        return {"valid": validation["valid"], "diagnostics": diagnostics, "next": self._next_steps(validation)}

    def command_schema(self) -> dict[str, Any]:
        return command_schema()

    def _validate_map(self, path: Path, errors: list[dict[str, Any]], warnings: list[dict[str, Any]]) -> None:
        try: data = self._read_json(path)
        except Exception as exc:
            errors.append(Diagnostic("error", "invalid_map_json", str(exc), str(path.relative_to(self.root)), "Fix the JSON syntax.").to_dict()); return
        if not isinstance(data, dict): errors.append(Diagnostic("error", "invalid_map", "Map root must be an object.", str(path.relative_to(self.root))).to_dict()); return
        nodes, connections, entities = data.get("nodes", []), data.get("connections", []), data.get("entities", [])
        if not isinstance(nodes, list): errors.append(Diagnostic("error", "invalid_nodes", "nodes must be an array.", "map.json.nodes").to_dict()); nodes = []
        if not isinstance(connections, list): errors.append(Diagnostic("error", "invalid_connections", "connections must be an array.", "map.json.connections").to_dict()); connections = []
        if not isinstance(entities, list): errors.append(Diagnostic("error", "invalid_entities", "entities must be an array.", "map.json.entities").to_dict()); entities = []
        node_ids: set[Any] = set(); entity_ids: set[Any] = set()
        for i, node in enumerate(nodes):
            if not isinstance(node, dict) or not node.get("id"): errors.append(Diagnostic("error", "invalid_node", "Node requires an id.", f"map.json.nodes[{i}]").to_dict()); continue
            if node["id"] in node_ids: errors.append(Diagnostic("error", "duplicate_node", f"Duplicate node id: {node['id']}", f"map.json.nodes[{i}]").to_dict())
            node_ids.add(node["id"])
        for i, c in enumerate(connections):
            if not isinstance(c, dict) or c.get("source") not in node_ids or c.get("target") not in node_ids: errors.append(Diagnostic("error", "invalid_connection", "Connection references an unknown node.", f"map.json.connections[{i}]").to_dict())
        for i, entity in enumerate(entities):
            if not isinstance(entity, dict) or not entity.get("id"): errors.append(Diagnostic("error", "invalid_entity", "Entity requires an id.", f"map.json.entities[{i}]").to_dict()); continue
            if entity["id"] in entity_ids: errors.append(Diagnostic("error", "duplicate_entity", f"Duplicate entity id: {entity['id']}", f"map.json.entities[{i}]").to_dict())
            entity_ids.add(entity["id"])
            if entity.get("node_id") not in node_ids: errors.append(Diagnostic("error", "unknown_entity_node", "Entity references an unknown node.", f"map.json.entities[{i}]").to_dict())
        if not nodes: warnings.append(Diagnostic("warning", "empty_map", "Map contains no nodes.", "map.json", "Add at least one node.").to_dict())

    @staticmethod
    def _read_json(path: Path) -> dict[str, Any]:
        with path.open("r", encoding="utf-8") as handle: return json.load(handle)

    @staticmethod
    def _exception_diagnostic(exc: Exception) -> Diagnostic:
        return Diagnostic("error", type(exc).__name__.lower(), str(exc) or type(exc).__name__, suggestion="Correct the reported operation and retry.")

    @staticmethod
    def _next_steps(validation: dict[str, Any]) -> list[str]:
        if validation["errors"]: return [item.get("suggestion", "Fix the reported diagnostic.") for item in validation["errors"][:3]]
        return ["Project is structurally valid.", "Continue using batch authoring commands."]
