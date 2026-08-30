from __future__ import annotations

from typing import Any, Callable


_COMMANDS: dict[str, tuple[str, tuple[str, ...]]] = {
    "start": ("Start the project runtime.", ()),
    "stop": ("Stop the project runtime.", ()),
    "switch_scene": ("Replace the scene stack with one scene.", ("scene_id",)),
    "push_scene": ("Push a temporary scene on the stack.", ("scene_id",)),
    "pop_scene": ("Return to the previous scene.", ()),
}


class AIProjectAPI:
    """Stable, JSON-safe facade for coding agents working with the engine."""

    def __init__(self, runtime: Any):
        self.runtime = runtime

    def describe(self) -> dict[str, Any]:
        return {
            "engine": "pynovel-engine",
            "api_version": 1,
            "runtime_running": bool(self.runtime.running),
            "scene": self.runtime.scene_id,
            "scene_stack": list(self.runtime.stack.ids()),
            "capabilities": [
                "project_introspection", "scenes", "scene_stack", "transitions",
                "input", "update", "render", "save_load", "commands"
            ],
        }

    def command_schema(self) -> dict[str, Any]:
        return {
            "api_version": 1,
            "commands": {
                name: {"description": description, "required": list(required)}
                for name, (description, required) in _COMMANDS.items()
            },
        }

    def scenes(self) -> list[str]:
        return list(self.runtime.scenes.ids())

    def inspect_scene(self, scene_id: str | None = None) -> dict[str, Any]:
        scene = self.runtime.scene if scene_id is None or scene_id == self.runtime.scene_id else None
        if scene is None:
            return {"id": scene_id, "active": False}
        methods = [
            name for name in (
                "enter", "exit", "pause", "resume", "update",
                "handle_input", "render", "serialize", "deserialize"
            ) if callable(getattr(scene, name, None))
        ]
        return {
            "id": self.runtime.scene_id,
            "active": True,
            "type": type(scene).__name__,
            "methods": methods,
        }

    def state(self) -> dict[str, Any]:
        return self.runtime.save_state()

    def call(self, command: str, **kwargs: Any) -> Any:
        spec = _COMMANDS.get(command)
        if spec is None:
            raise ValueError(f"Unsupported AI command: {command}")
        required = spec[1]
        missing = [name for name in required if name not in kwargs]
        if missing:
            raise ValueError(f"Missing required arguments for {command}: {', '.join(missing)}")
        handlers: dict[str, Callable[..., Any]] = {
            "start": self.runtime.start,
            "stop": self.runtime.stop,
            "switch_scene": self.runtime.switch_scene,
            "push_scene": self.runtime.push_scene,
            "pop_scene": self.runtime.pop_scene,
        }
        if set(kwargs) - set(required):
            extra = sorted(set(kwargs) - set(required))
            raise ValueError(f"Unexpected arguments for {command}: {', '.join(extra)}")
        return handlers[command](**kwargs)
