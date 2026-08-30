from __future__ import annotations

import shlex
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .project_document import ProjectDocument


class DSLParseError(ValueError):
    def __init__(self, message: str, *, line: int):
        super().__init__(f"line {line}: {message}")
        self.line = line


@dataclass(frozen=True, slots=True)
class DSLDocument:
    project: dict[str, Any]
    scenes: dict[str, dict[str, Any]]


class GameDSL:
    """Small indentation-insensitive game description language for AI authors."""

    def parse(self, text: str) -> DSLDocument:
        project: dict[str, Any] = {"version": "1.0", "map_path": "map.json", "start_scene": "main"}
        scenes: dict[str, dict[str, Any]] = {}
        current_scene: dict[str, Any] | None = None

        for line_no, raw in enumerate(text.splitlines(), 1):
            stripped = raw.strip()
            if not stripped or stripped.startswith("#"): continue
            try: tokens = shlex.split(stripped)
            except ValueError as exc: raise DSLParseError(str(exc), line=line_no) from exc
            command = tokens[0]
            args = tokens[1:]
            try:
                if command == "project":
                    self._expect(args, 1, command); project["name"] = args[0]
                elif command == "version":
                    self._expect(args, 1, command); project["version"] = args[0]
                elif command == "start":
                    self._expect(args, 1, command); project["start_scene"] = args[0]
                elif command == "map":
                    self._expect(args, 2, command); project["map"] = {"width": float(args[0]), "height": float(args[1]), "nodes": [], "connections": [], "entities": []}
                elif command == "scene":
                    self._expect(args, 1, command)
                    scene = {"id": args[0], "actions": []}
                    scenes[args[0]] = scene; current_scene = scene
                elif command == "background":
                    self._scene(current_scene, line_no)["background"] = args[0] if args else self._error("background requires a value", line_no)
                elif command == "character":
                    self._expect(args, 1, command); self._scene(current_scene, line_no)["actions"].append({"type": "character", "id": args[0]})
                elif command == "say":
                    self._expect(args, 2, command); self._scene(current_scene, line_no)["actions"].append({"type": "say", "speaker": args[0], "text": " ".join(args[1:])})
                elif command == "choice":
                    if len(args) < 3 or args[-2] != "->": self._error("choice syntax is: choice \"Text\" -> scene", line_no)
                    self._scene(current_scene, line_no)["actions"].append({"type": "choice", "text": " ".join(args[:-2]), "target": args[-1]})
                elif command == "node":
                    self._expect(args, 3, command); project.setdefault("map", {"width": 1200, "height": 700, "nodes": [], "connections": [], "entities": []})["nodes"].append({"id": args[0], "x": float(args[1]), "y": float(args[2]), "label": args[3] if len(args) > 3 else args[0]})
                elif command == "connect":
                    self._expect(args, 2, command); project.setdefault("map", {"width": 1200, "height": 700, "nodes": [], "connections": [], "entities": []})["connections"].append({"source": args[0], "target": args[1], "cost": 1.0, "blocked": False})
                elif command == "entity":
                    self._expect(args, 2, command); project.setdefault("map", {"width": 1200, "height": 700, "nodes": [], "connections": [], "entities": []})["entities"].append({"id": args[0], "node_id": args[1], "components": {}})
                else: self._error(f"unknown command: {command}", line_no)
            except DSLParseError: raise
            except (TypeError, ValueError) as exc: raise DSLParseError(str(exc), line=line_no) from exc
        if "name" not in project: raise DSLParseError("project name is required", line=1)
        return DSLDocument(project=project, scenes=scenes)

    def compile(self, text: str, root: str | Path, *, save: bool = True) -> dict[str, Any]:
        parsed = self.parse(text)
        document = ProjectDocument(root)
        document.data.update({key: value for key, value in parsed.project.items() if key != "map"})
        if "map" in parsed.project: document.data["map"] = parsed.project["map"]
        document.data["scenes"] = parsed.scenes
        if save: document.save()
        return {"project": document.manifest(), "scenes": sorted(parsed.scenes), "map": document.inspect()["map"]}

    @staticmethod
    def _expect(args: list[str], minimum: int, command: str) -> None:
        if len(args) < minimum: raise ValueError(f"{command} requires at least {minimum} argument(s)")

    @staticmethod
    def _scene(scene: dict[str, Any] | None, line_no: int) -> dict[str, Any]:
        if scene is None: raise DSLParseError("command requires an active scene", line=line_no)
        return scene

    @staticmethod
    def _error(message: str, line_no: int): raise DSLParseError(message, line=line_no)
