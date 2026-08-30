from __future__ import annotations

import inspect
from typing import Any


class AIProjectAPI:
    """Small, JSON-safe introspection facade intended for coding agents."""
    def __init__(self, runtime: Any):
        self.runtime = runtime

    def describe(self) -> dict[str, Any]:
        """Return stable engine capabilities without exposing implementation details."""
        return {
            "engine": "pynovel-engine",
            "api_version": 1,
            "scene": self.runtime.scene_id,
            "scene_stack": list(self.runtime.stack.ids()),
            "capabilities": ["scenes", "scene_stack", "transitions", "input", "update", "render", "save_load"],
        }

    def scenes(self) -> list[str]:
        registry = self.runtime.scenes
        return sorted(getattr(registry, "_factories", {}).keys())

    def inspect_scene(self, scene_id: str | None = None) -> dict[str, Any]:
        scene = self.runtime.scene if scene_id is None or scene_id == self.runtime.scene_id else None
        if scene is None:
            return {"id": scene_id, "active": False}
        methods = [name for name in ("enter", "exit", "pause", "resume", "update", "handle_input", "render", "serialize", "deserialize") if callable(getattr(scene, name, None))]
        return {"id": self.runtime.scene_id, "active": True, "type": type(scene).__name__, "methods": methods}

    def state(self) -> dict[str, Any]:
        return self.runtime.save_state()

    def call(self, command: str, **kwargs: Any) -> Any:
        """Invoke only an explicitly whitelisted runtime operation."""
        allowed = {
            "start": self.runtime.start,
            "stop": self.runtime.stop,
            "switch_scene": self.runtime.switch_scene,
            "push_scene": self.runtime.push_scene,
            "pop_scene": self.runtime.pop_scene,
        }
        if command not in allowed:
            raise ValueError(f"Unsupported AI command: {command}")
        return allowed[command](**kwargs)
