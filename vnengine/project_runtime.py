from __future__ import annotations
from typing import Any
from .project import ProjectLoader
from .scene_registry import SceneRegistry, SceneContext


class ProjectRuntime:
    """Lifecycle wrapper for data-driven projects with extensible scenes."""
    def __init__(self, project: str, *, emit=None, scenes: SceneRegistry | None = None):
        self.project = ProjectLoader(project)
        self.emit = emit or (lambda name, data: None)
        self.scenes = scenes or SceneRegistry()
        self.world = None; self.scene_id: str | None = None; self.scene: Any = None; self.running = False
        if not self.scenes.has("map"):
            self.scenes.register("map", lambda context: context.runtime.project.load_map(emit=context.runtime.emit))

    def start(self) -> None:
        self.switch_scene(self.project.manifest.start_scene)
        self.running = True; self.emit("runtime.started", {"scene": self.scene_id})

    def switch_scene(self, scene_id: str) -> Any:
        previous = self.scene_id
        scene = self.scenes.create(scene_id, self)
        self.scene_id = scene_id; self.scene = scene
        self.world = getattr(scene, "world", scene)
        self.emit("scene.changed", {"from": previous, "to": scene_id})
        return scene

    def update(self, dt: float) -> None:
        if not self.running or self.scene is None: return
        update = getattr(self.scene, "update", None)
        if callable(update): update(max(0.0, float(dt)))

    def stop(self) -> None:
        self.running = False; self.emit("runtime.stopped", {})

    def save_state(self) -> dict[str, Any]:
        saver = getattr(self.scene, "serialize", None)
        return {"scene": self.scene_id, "world": saver() if callable(saver) else (self.world.serialize() if self.world is not None else None)}

    def load_state(self, state: dict[str, Any]) -> None:
        self.switch_scene(state.get("scene", self.project.manifest.start_scene))
        if state.get("world") is not None and self.world is not None: self.world.deserialize(state["world"])
        self.running = True; self.emit("runtime.loaded", {"scene": self.scene_id})
