from __future__ import annotations
from typing import Any
from .project import ProjectLoader


class ProjectRuntime:
    """Small lifecycle wrapper for data-driven engine projects."""
    def __init__(self, project: str, *, emit=None):
        self.project = ProjectLoader(project)
        self.emit = emit or (lambda name, data: None)
        self.world = None
        self.scene_id: str | None = None
        self.running = False

    def start(self) -> None:
        self.scene_id = self.project.manifest.start_scene
        if self.scene_id != "map":
            raise ValueError(f"Unsupported start scene: {self.scene_id}")
        self.world = self.project.load_map(emit=self.emit)
        self.running = True
        self.emit("runtime.started", {"scene": self.scene_id})

    def update(self, dt: float) -> None:
        if self.running and self.world is not None:
            self.world.update(max(0.0, float(dt)))

    def stop(self) -> None:
        self.running = False
        self.emit("runtime.stopped", {})

    def save_state(self) -> dict[str, Any]:
        return {"scene": self.scene_id, "world": self.world.serialize() if self.world is not None else None}

    def load_state(self, state: dict[str, Any]) -> None:
        scene = state.get("scene", self.project.manifest.start_scene)
        if scene != "map": raise ValueError(f"Unsupported scene: {scene}")
        if self.world is None: self.world = self.project.load_map(emit=self.emit)
        self.scene_id = scene
        if state.get("world") is not None: self.world.deserialize(state["world"])
        self.running = True
        self.emit("runtime.loaded", {"scene": scene})
