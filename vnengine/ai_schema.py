from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class CommandSpec:
    name: str
    description: str
    required: tuple[str, ...] = ()
    optional: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


COMMANDS = (
    CommandSpec("start", "Start the project runtime."),
    CommandSpec("stop", "Stop the project runtime."),
    CommandSpec("switch_scene", "Replace the scene stack with one scene.", ("scene_id",), ("transition",)),
    CommandSpec("push_scene", "Push a temporary scene on the stack.", ("scene_id",), ("transition",)),
    CommandSpec("pop_scene", "Remove the current temporary scene.", (), ("transition",)),
)


def command_schema() -> dict[str, Any]:
    return {"api_version": 1, "commands": {spec.name: spec.to_dict() for spec in COMMANDS}}
