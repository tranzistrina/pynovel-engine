from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .ai import AIProjectAPI
from .ai_builder import AIProjectBuilder


@dataclass(frozen=True, slots=True)
class Diagnostic:
    severity: str
    code: str
    message: str
    path: str | None = None
    suggestion: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {key: value for key, value in {
            "severity": self.severity,
            "code": self.code,
            "message": self.message,
            "path": self.path,
            "suggestion": self.suggestion,
        }.items() if value is not None}


class AIAgentInterface:
    """Unified, deterministic authoring and diagnostics facade for coding agents."""
    API_VERSION = 1

    def __init__(self, root: str | Path, *, runtime: Any = None):
        self.root = Path(root).resolve()
        self.builder = AIProjectBuilder(self.root)
        self.runtime = runtime
        self.runtime_api = AIProjectAPI(runtime) if runtime is not None else None

    def capabilities(self) -> dict[str, Any]:
        commands = [
            "create_project", "create_map", "add_node", "add_connection", "add_entity",
            "set_map_property", "set_entity_property", "remove_node", "remove_entity",
        ]
        return {"api_version": self.API_VERSION, "features": ["authoring", "batch", "inspect", "validate", "diagnostics"], "commands": commands}

    def inspect(self) -> dict[str, Any]:
        result = self.builder.inspect()
        if self.runtime_api is not None:
            result["runtime"] = self.runtime_api.describe()["runtime"]
        return result

    def validate(self) -> dict[str, Any]:
        errors: list[dict[str, Any]] = []
        warnings: list[dict[str, Any]] = []
        manifest_path = self.root / "project.json"
        if not manifest_path.is_file():
            errors.append(Diagnostic("error", "missing_manifest", "Project manifest is missing.", "project.json", "Create the project before adding game content.").to_dict())
            return {"valid": False, "errors": errors, "warnings": warnings}
        try:
            result = self.runtime_api.validate() if self.runtime_api is not None else self._validate_disk_project()
            errors.extend(result["errors"]); warnings.extend(result["warnings"])
        except Exception as exc:
            errors.append(Diagnostic("error", "validation_exception", str(exc), None, "Inspect the project files and rerun validation.").to_dict())
        return {"valid": not errors, "errors": errors, "warnings": warnings}

    def diagnose(self) -> dict[str, Any]:
        validation = self.validate()
        return {"valid": validation["valid"], "diagnostics": validation["errors"] + validation["warnings"], "next": self._next_steps(validation)}

    def apply(self, operations: list[dict[str, Any]], *, save: bool = True, validate: bool = True) -> dict[str, Any]:
        result = self.builder.apply(operations, save=save)
        if validate:
            validation = self.validate()
            if not validation["valid"]:
                raise ValueError(f"Project invalid after apply: {validation['errors'][0]['message']}")
            result["validation"] = validation
        return result

    def _validate_disk_project(self) -> dict[str, Any]:
        import json
        manifest = json.loads((self.root / "project.json").read_text(encoding="utf-8"))
        errors: list[dict[str, Any]] = []
        warnings: list[dict[str, Any]] = []
        map_path = self.root / str(manifest.get("map_path", "map.json"))
        if not map_path.is_file():
            errors.append(Diagnostic("error", "missing_map", "Configured map file is missing.", str(map_path.relative_to(self.root)), "Create a map or correct map_path.").to_dict())
        if not manifest.get("name"):
            errors.append(Diagnostic("error", "missing_name", "Project name is missing.", "project.json", "Set a non-empty project name.").to_dict())
        return {"valid": not errors, "errors": errors, "warnings": warnings}

    @staticmethod
    def _next_steps(validation: dict[str, Any]) -> list[str]:
        if not validation["valid"]:
            return [item.get("suggestion", "Fix the reported diagnostic.") for item in validation["errors"][:3]]
        return ["Project is structurally valid.", "Create gameplay content through batch authoring commands."]
