from __future__ import annotations
from typing import Any
from .project import ProjectLoader
from .scene_registry import SceneRegistry, SceneContext
from .scene_stack import SceneStack
from .transition import TransitionManager


class ProjectRuntime:
    """Lifecycle wrapper for data-driven projects with extensible scenes."""
    def __init__(self, project: str, *, emit=None, scenes: SceneRegistry | None = None, viewport: Any = None, frontend: Any = None):
        self.project = ProjectLoader(project); self.emit = emit or (lambda name, data: None)
        self.scenes = scenes or SceneRegistry(); self.stack = SceneStack(); self.transitions = TransitionManager()
        self.viewport = viewport; self.frontend = frontend
        self.world = None; self.scene_id: str | None = None; self.scene: Any = None; self.running = False
        if not self.scenes.has("map"):
            self.scenes.register("map", self._create_map_scene)

    def _create_map_scene(self, context: SceneContext) -> Any:
        from .map.loader import load_playable_map
        from .map.scene import MapScene
        path = context.runtime.project.root / "map.json"
        game_map = load_playable_map(path, emit=context.runtime.emit)
        viewport = context.runtime.viewport
        if viewport is None and context.runtime.frontend is not None: viewport = context.runtime.frontend.screen.get_rect()
        if viewport is None: raise RuntimeError("Map scene requires a viewport")
        return MapScene(game_map, viewport, pygame_module=getattr(context.runtime.frontend, "_pygame", None), emit=context.runtime.emit)

    def start(self, *, transition: tuple[str, float] | None = None) -> None:
        self.switch_scene(self.project.manifest.start_scene, transition=transition); self.running = True
        self.emit("runtime.started", {"scene": self.scene_id})

    def switch_scene(self, scene_id: str, *, transition: tuple[str, float] | None = None) -> Any:
        previous = self.scene_id
        if transition: self.transitions.start(*transition)
        if self.scene is not None: self._call(self.scene, "exit")
        scene = self.scenes.create(scene_id, self); self.stack.clear(); self.stack.push(scene_id, scene)
        self.scene_id = scene_id; self.scene = scene; self.world = getattr(scene, "world", scene); self._call(scene, "enter")
        self.emit("scene.changed", {"from": previous, "to": scene_id}); return scene

    def push_scene(self, scene_id: str, *, transition: tuple[str, float] | None = None) -> Any:
        if transition: self.transitions.start(*transition)
        if self.scene is not None: self._call(self.scene, "pause")
        scene = self.scenes.create(scene_id, self); self.stack.push(scene_id, scene); self.scene_id = scene_id
        self.scene = scene; self.world = getattr(scene, "world", scene); self._call(scene, "enter")
        self.emit("scene.pushed", {"scene": scene_id}); return scene

    def pop_scene(self, *, transition: tuple[str, float] | None = None) -> Any:
        if len(self.stack) <= 1: raise IndexError("Cannot pop the root scene")
        if transition: self.transitions.start(*transition)
        self._call(self.scene, "exit"); self.stack.pop(); self.scene_id = self.stack.current_id
        self.scene = self.stack.current; self.world = getattr(self.scene, "world", self.scene); self._call(self.scene, "resume")
        self.emit("scene.popped", {"scene": self.scene_id}); return self.scene

    def handle_input(self, event: Any) -> bool:
        if not self.running or self.scene is None: return False
        handler = getattr(self.scene, "handle_input", None)
        return bool(handler(event)) if callable(handler) else False

    def render(self, target: Any) -> None:
        if self.scene is None: return
        renderer = getattr(self.scene, "render", None)
        if callable(renderer): renderer(target)

    def update(self, dt: float) -> None:
        if not self.running or self.scene is None: return
        self.transitions.update(dt); update = getattr(self.scene, "update", None)
        if callable(update): update(max(0.0, float(dt)))

    def stop(self) -> None:
        if self.scene is not None: self._call(self.scene, "exit")
        self.running = False; self.emit("runtime.stopped", {})

    def save_state(self) -> dict[str, Any]:
        saver = getattr(self.scene, "serialize", None)
        return {"scene_stack": list(self.stack.ids()), "scene": self.scene_id, "world": saver() if callable(saver) else (self.world.serialize() if self.world is not None else None)}

    def load_state(self, state: dict[str, Any]) -> None:
        ids = state.get("scene_stack") or [state.get("scene", self.project.manifest.start_scene)]
        self.switch_scene(ids[0])
        for scene_id in ids[1:]: self.push_scene(scene_id)
        if state.get("world") is not None and self.world is not None: self.world.deserialize(state["world"])
        self.running = True; self.emit("runtime.loaded", {"scene": self.scene_id})

    @staticmethod
    def _call(scene: Any, method: str) -> None:
        callback = getattr(scene, method, None)
        if callable(callback): callback()
