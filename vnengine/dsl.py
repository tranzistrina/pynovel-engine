from __future__ import annotations

import json
import shlex
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .project_document import ProjectDocument


class DSLParseError(ValueError):
    def __init__(self, message: str, *, line: int):
        self.line = line
        super().__init__(f"line {line}: {message}")


@dataclass(frozen=True, slots=True)
class DSLDocument:
    project: dict[str, Any]
    scenes: dict[str, dict[str, Any]]


class GameDSL:
    """Compact, forgiving game language intended for AI-generated projects."""

    @staticmethod
    def _default_map() -> dict[str, Any]:
        return {"width": 1200, "height": 700, "nodes": [], "connections": [], "entities": []}

    def parse(self, text: str) -> DSLDocument:
        project: dict[str, Any] = {"version": "1.0", "map_path": "map.json", "start_scene": "main", "variables": {}}
        scenes: dict[str, dict[str, Any]] = {}
        current_scene: dict[str, Any] | None = None

        for line_no, raw in enumerate(text.splitlines(), 1):
            stripped = raw.strip()
            if not stripped or stripped.startswith("#"):
                continue
            try:
                tokens = shlex.split(stripped)
            except ValueError as exc:
                raise DSLParseError(str(exc), line=line_no) from exc
            command, args = tokens[0], tokens[1:]
            try:
                if command == "project":
                    self._expect(args, 1, command); project["name"] = args[0]
                elif command == "version":
                    self._expect(args, 1, command); project["version"] = args[0]
                elif command == "start":
                    self._expect(args, 1, command); project["start_scene"] = args[0]
                elif command == "var":
                    self._set_variable(project, args, line_no)
                elif command == "map":
                    self._expect(args, 2, command)
                    project["map"] = {"width": float(args[0]), "height": float(args[1]), "nodes": [], "connections": [], "entities": []}
                elif command == "scene":
                    self._expect(args, 1, command)
                    if args[0] in scenes:
                        raise ValueError(f"duplicate scene: {args[0]}")
                    scene = {"id": args[0], "actions": []}
                    scenes[args[0]] = scene
                    current_scene = scene
                elif command == "background":
                    self._scene(current_scene, line_no)["background"] = self._value(args, line_no, "background")
                elif command == "character":
                    self._expect(args, 1, command); self._add_action(current_scene, line_no, {"type": "character", "id": args[0]})
                elif command == "say":
                    self._expect(args, 2, command); self._add_action(current_scene, line_no, {"type": "say", "speaker": args[0], "text": " ".join(args[1:])})
                elif command == "set":
                    self._add_action(current_scene, line_no, {"type": "set", "variable": self._arg(args, 0, line_no), "value": self._value(args[1:], line_no, "set")})
                elif command == "change":
                    self._add_action(current_scene, line_no, {"type": "change", "variable": self._arg(args, 0, line_no), "amount": float(self._arg(args, 1, line_no))})
                elif command == "emit":
                    self._add_action(current_scene, line_no, {"type": "emit", "name": self._arg(args, 0, line_no), "data": self._parse_object(args[1:], line_no) if len(args) > 1 else {}})
                elif command == "label":
                    self._add_action(current_scene, line_no, {"type": "label", "label": self._arg(args, 0, line_no)})
                elif command == "goto":
                    self._add_action(current_scene, line_no, {"type": "goto", "target": self._arg(args, 0, line_no)})
                elif command == "if":
                    self._parse_if(current_scene, args, line_no)
                elif command == "choice":
                    self._parse_choice(current_scene, args, line_no)
                elif command == "node":
                    self._expect(args, 3, command)
                    project.setdefault("map", self._default_map())["nodes"].append({"id": args[0], "x": float(args[1]), "y": float(args[2]), "label": args[3] if len(args) > 3 else args[0]})
                elif command == "connect":
                    self._expect(args, 2, command)
                    project.setdefault("map", self._default_map())["connections"].append({"source": args[0], "target": args[1], "cost": 1.0, "blocked": False})
                elif command == "entity":
                    self._expect(args, 2, command)
                    project.setdefault("map", self._default_map())["entities"].append({"id": args[0], "node_id": args[1], "components": {}})
                else:
                    self._error(f"unknown command: {command}", line_no)
            except DSLParseError:
                raise
            except (TypeError, ValueError) as exc:
                raise DSLParseError(str(exc), line=line_no) from exc

        if "name" not in project:
            raise DSLParseError("project name is required", line=1)
        return DSLDocument(project=project, scenes=scenes)

    def compile(self, text: str, root: str | Path, *, save: bool = True) -> dict[str, Any]:
        parsed = self.parse(text)
        document = ProjectDocument(root)
        document.data.update({key: value for key, value in parsed.project.items() if key != "map"})
        if "map" in parsed.project:
            document.data["map"] = parsed.project["map"]
        document.data["scenes"] = parsed.scenes
        if save:
            document.save()
        return {"project": document.manifest(), "scenes": sorted(parsed.scenes), "map": document.inspect()["map"]}

    @staticmethod
    def _set_variable(project: dict[str, Any], args: list[str], line_no: int) -> None:
        if len(args) < 2:
            raise DSLParseError("var syntax is: var name value", line=line_no)
        project.setdefault("variables", {})[args[0]] = GameDSL._value(args[1:], line_no, "var")

    @staticmethod
    def _parse_choice(scene: dict[str, Any] | None, args: list[str], line_no: int) -> None:
        scene = GameDSL._scene(scene, line_no)
        if "->" not in args:
            raise DSLParseError('choice syntax is: choice "Text" [if variable op value] -> target', line=line_no)
        arrow = args.index("->")
        if arrow < 1 or arrow == len(args) - 1:
            raise DSLParseError('choice syntax is: choice "Text" [if variable op value] -> target', line=line_no)
        left, target = args[:arrow], args[arrow + 1]
        data: dict[str, Any] = {"type": "choice", "text": " ".join(left), "target": target}
        if "if" in left:
            i = left.index("if")
            condition = left[i + 1:]
            if len(condition) != 3:
                raise DSLParseError("choice condition syntax is: if variable op value", line=line_no)
            data["condition"] = {"variable": condition[0], "operator": condition[1], "value": GameDSL._value([condition[2]], line_no, "choice")}
            data["text"] = " ".join(left[:i])
        scene["actions"].append(data)

    @staticmethod
    def _parse_if(scene: dict[str, Any] | None, args: list[str], line_no: int) -> None:
        scene = GameDSL._scene(scene, line_no)
        if len(args) != 5 or args[3] != "->":
            raise DSLParseError("if syntax is: if variable op value -> label", line=line_no)
        scene["actions"].append({"type": "if", "condition": {"variable": args[0], "operator": args[1], "value": GameDSL._value([args[2]], line_no, "if")}, "then": [{"type": "goto", "target": args[4]}]})

    @staticmethod
    def _parse_object(args: list[str], line_no: int) -> dict[str, Any]:
        value = GameDSL._value(args, line_no, "emit data")
        if not isinstance(value, dict):
            raise DSLParseError("emit data must be an object", line=line_no)
        return value

    @staticmethod
    def _value(args: list[str], line_no: int, command: str) -> Any:
        if not args:
            raise DSLParseError(f"{command} requires a value", line=line_no)
        raw = " ".join(args)
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return raw

    @staticmethod
    def _arg(args: list[str], index: int, line_no: int) -> str:
        if len(args) <= index:
            raise DSLParseError("missing argument", line=line_no)
        return args[index]

    @staticmethod
    def _add_action(scene: dict[str, Any] | None, line_no: int, action: dict[str, Any]) -> None:
        GameDSL._scene(scene, line_no)["actions"].append(action)

    @staticmethod
    def _expect(args: list[str], minimum: int, command: str) -> None:
        if len(args) < minimum:
            raise ValueError(f"{command} requires at least {minimum} argument(s)")

    @staticmethod
    def _scene(scene: dict[str, Any] | None, line_no: int) -> dict[str, Any]:
        if scene is None:
            raise DSLParseError("command requires an active scene", line=line_no)
        return scene

    @staticmethod
    def _error(message: str, line_no: int) -> None:
        raise DSLParseError(message, line=line_no)
