from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .ai import AIProjectAPI
from .ai_builder import AIProjectBuilder
from .ai_schema import command_schema


@dataclass(frozen=True, slots=True)
class Diagnostic:
    severity: str
    code: str
    message: str
    path: str | None = None
    suggestion: str | None = None

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {"severity": self.severity, "code": self.code, "message": self.message}
        if self.path is not None: data["path"] = self.path
        if self.suggestion is not None: data["suggestion"] = self.suggestion
        return data


class AIAgentInterface:
    """Single stable API for AI agents to inspect, plan, mutate and diagnose projects."""

    API_VERSION = 3
    BUILDER_COMMANDS = {
        "create_project": {"required": ["name"], "optional": ["version", "map_path", "start_scene"]},
        "create_map": {"required": ["width", "height"], "optional": ["background"]},
        "add_node": {"required": ["node_id", "x", "y"], "optional": ["label", "metadata"]},
        "add_connection": {"required": ["source", "target"], "optional": ["cost", "blocked", "metadata"]},
        "add_entity": {"required": ["entity_id", "node_id"], "optional": ["components"]},
        "set_map_property": {"required": ["key", "value"], "optional": []},
        "set_entity_property": {"required": ["entity_id", "key", "value"], "optional": []},
        "remove_node": {"required": ["node_id"], "optional": []},
        "remove_entity": {"required": ["entity_id"], "optional": []},
    }

    def __init__(self, root: str | Path, *, runtime: Any = None):
        self.root = Path(root).resolve()
        self.builder = AIProjectBuilder(self.root)
        self.runtime = runtime
        self.runtime_api = AIProjectAPI(runtime) if runtime is not None else None

    def capabilities(self) -> dict[str, Any]:
        return {"api_version": self.API_VERSION, "features": ["inspect", "plan", "dry_run", "apply", "validate", "diagnose"], "project_commands": sorted(self.BUILDER_COMMANDS), "runtime_commands": list(command_schema()["commands"])}

    def inspect(self) -> dict[str, Any]:
        result = self.builder.inspect()
        if self.runtime_api is not None: result["runtime"] = self.runtime_api.describe()["runtime"]
        return result

    def plan(self, operations: list[dict[str, Any]]) -> dict[str, Any]:
        diagnostics: list[dict[str, Any]] = []
        for index, operation in enumerate(operations):
            location = f"operations[{index}]"
            if not isinstance(operation, dict):
                diagnostics.append(Diagnostic("error", "invalid_operation", "Operation must be an object.", location).to_dict()); continue
            command = operation.get("command"); spec = self.BUILDER_COMMANDS.get(command)
            if spec is None:
                diagnostics.append(Diagnostic("error", "unknown_command", f"Unsupported builder command: {command}", f"{location}.command").to_dict()); continue
            for name in spec["required"]:
                if name not in operation: diagnostics.append(Diagnostic("error", "missing_argument", f"Missing required argument: {name}", f"{location}.{name}").to_dict())
            allowed = set(spec["required"]) | set(spec["optional"]) | {"command"}
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
        self.builder.document.rollback()
        return {"committed": False, "applied": len(results), "before": before, "preview": preview, "plan": plan, "diagnostics": []}

    def apply(self, operations: list[dict[str, Any]], *, save: bool = True, validate: bool = True) -> dict[str, Any]:
        plan = self.plan(operations)
        if not plan["valid"]: return {"committed": False, "applied": 0, "plan": plan, "diagnostics": plan["diagnostics"]}
        try: result = self.builder.apply(operations, save=save)
        except Exception as exc: return {"committed": False, "applied": 0, "plan": plan, "diagnostics": [self._exception_diagnostic(exc).to_dict()]}
        validation = self.validate() if validate else {"valid": True, "errors": [], "warnings": []}
        result.update({"committed": True, "validation": validation, "diagnostics": validation["errors"] + validation["warnings"]})
        return result

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
        elif self.runtime is not None:
            start = manifest.get("start_scene")
            if start and not self.runtime.scenes.has(start): errors.append(Diagnostic("error", "unknown_start_scene", f"Start scene is not registered: {start}", "project.json").to_dict())
        return {"valid": not errors, "errors": errors, "warnings": warnings}

    def diagnose(self) -> dict[str, Any]:
        validation = self.validate(); diagnostics = validation["errors"] + validation["warnings"]
        return {"valid": validation["valid"], "diagnostics": diagnostics, "next": self._next_steps(validation)}

    def command_schema(self) -> dict[str, Any]:
        schema = command_schema(); schema["builder_commands"] = self.BUILDER_COMMANDS; return schema

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
