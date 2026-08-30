from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class CommandSpec:
    name: str
    description: str
    required: tuple[str, ...] = ()
    optional: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]: return asdict(self)


RUNTIME_COMMANDS = (
    CommandSpec("start", "Start the project runtime."),
    CommandSpec("stop", "Stop the project runtime."),
    CommandSpec("switch_scene", "Replace the scene stack with one scene.", ("scene_id",), ("transition",)),
    CommandSpec("push_scene", "Push a temporary scene on the stack.", ("scene_id",), ("transition",)),
    CommandSpec("pop_scene", "Remove the current temporary scene.", (), ("transition",)),
)

BUILDER_COMMANDS = (
    CommandSpec("create_project", "Create or replace the project manifest.", ("name",), ("version", "map_path", "start_scene", "variables")),
    CommandSpec("set_variable", "Set an initial project variable.", ("key", "value")),
    CommandSpec("create_map", "Create or reset the project map.", ("width", "height"), ("background",)),
    CommandSpec("add_node", "Add a map node.", ("node_id", "x", "y"), ("label", "metadata")),
    CommandSpec("add_connection", "Connect two existing map nodes.", ("source", "target"), ("cost", "blocked", "metadata")),
    CommandSpec("add_entity", "Add an entity to an existing map node.", ("entity_id", "node_id"), ("components",)),
    CommandSpec("set_map_property", "Set a map property.", ("key", "value")),
    CommandSpec("set_entity_property", "Set an entity property.", ("entity_id", "key", "value")),
    CommandSpec("remove_node", "Remove an unused map node.", ("node_id",)),
    CommandSpec("remove_entity", "Remove a map entity.", ("entity_id",)),
    CommandSpec("add_scene", "Create a declarative scene.", ("scene_id",), ("background",)),
    CommandSpec("remove_scene", "Remove a non-start scene.", ("scene_id",)),
    CommandSpec("add_scene_action", "Append a raw declarative scene action.", ("scene_id", "action_type")),
    CommandSpec("say", "Append dialogue to a scene.", ("scene_id", "speaker", "text")),
    CommandSpec("choice", "Append a branching choice.", ("scene_id", "text", "target"), ("condition",)),
    CommandSpec("set_action", "Set a variable during scene execution.", ("scene_id", "variable", "value")),
    CommandSpec("change_action", "Change a numeric variable during scene execution.", ("scene_id", "variable"), ("amount",)),
    CommandSpec("goto", "Jump to a scene label.", ("scene_id", "target")),
    CommandSpec("label", "Create a jump label inside a scene.", ("scene_id", "name")),
)


def command_schema() -> dict[str, Any]: return {"api_version": 4, "runtime_commands": {s.name: s.to_dict() for s in RUNTIME_COMMANDS}, "builder_commands": {s.name: s.to_dict() for s in BUILDER_COMMANDS}}
