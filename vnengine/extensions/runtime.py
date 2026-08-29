from __future__ import annotations
from typing import Any
from vnengine.core.engine import Runtime as CoreRuntime
from vnengine.core.model import Action
from vnengine.core.rng import DeterministicRNG
from vnengine.core.save_bundle import SaveBundle
from vnengine.extensions.commands import CommandRegistry
from vnengine.extensions.events import EventBus
from vnengine.extensions.scenes import SceneStack
from vnengine.extensions.scheduler import GameScheduler
from vnengine.extensions.state import StateRegistry
from vnengine.extensions.system import SystemRegistry


class ExtensibleRuntime(CoreRuntime):
    """Core Runtime with opt-in project extension primitives."""

    ENGINE_VERSION = "0.32.0"

    def __init__(self, story, asset_root):
        super().__init__(story, asset_root)
        self.event_bus = EventBus(); self.systems = SystemRegistry(); self.commands = CommandRegistry()
        self.scene_stack = SceneStack(self); self.game_state = StateRegistry(); self.scheduler = GameScheduler(); self.rng = DeterministicRNG(0)
        self._register_builtin_extension_actions(); self.emit("project.startup", {"title": story.title})

    def _register_builtin_extension_actions(self) -> None:
        self._extension_handlers = {"call_system": self._call_system, "emit": self._emit_action, "set_state": self._set_state, "open_scene": self._open_scene, "close_scene": self._close_scene}
    def register_system(self, system) -> None: self.systems.register(system)
    def unregister_system(self, name: str) -> None: self.systems.unregister(name)
    def register_command(self, name: str, handler) -> None: self.commands.register(name, handler)
    def unregister_command(self, name: str) -> None: self.commands.unregister(name)
    def subscribe(self, event_name: str, callback, priority: int = 0): return self.event_bus.subscribe(event_name, callback, priority)
    def unsubscribe(self, subscription) -> None: self.event_bus.unsubscribe(subscription)
    def emit(self, event_name: str, data: dict[str, Any] | None = None) -> bool: return self.event_bus.emit(event_name, data)
    def register_state_namespace(self, name: str, initial=None, version: int = 1) -> None: self.game_state.register(name, initial, version)
    def get_state(self, path: str, default=None): return self.game_state.get(path, default)
    def set_state(self, path: str, value) -> None: self.game_state.set(path, value)
    def push_scene(self, scene, **kwargs) -> None: self.scene_stack.push(scene, **kwargs)
    def pop_scene(self): return self.scene_stack.pop()
    def replace_scene(self, scene, **kwargs) -> None: self.scene_stack.replace(scene, **kwargs)

    def update(self, dt: float) -> None:
        super().update(dt)
        for system in self.systems.values(): system.update(dt, self.game_state)
        self.scene_stack.update(dt)
        self.scheduler.advance(max(0, int(dt * self.scheduler.tick_rate)), lambda item: self.emit(item.event, item.data))

    def dispatch_input(self, event: object) -> bool:
        if self.scene_stack.handle_input(event): return True
        return any(system.handle_event(event, self.game_state) for system in self.systems.values())

    def _call_system(self, action: Action) -> None:
        system = self.systems.get(action.data["system"])
        if system is None: raise RuntimeError(f"Unknown game system: {action.data['system']}")
        method_name = action.data["method"]; method = getattr(system, method_name, None)
        if method is None or method_name.startswith("_"): raise RuntimeError(f"System method is not callable: {method_name}")
        method(*action.data.get("args", []))
    def _emit_action(self, action: Action) -> None: self.emit(action.data["event"], {"args": list(action.data.get("args", []))})
    def _set_state(self, action: Action) -> None:
        from vnengine.core.expressions import evaluate
        value = evaluate(action.data["expression"], self.state.variables); self.set_state(action.data["path"], value); self.emit("state.changed", {"path": action.data["path"], "value": value})
    def _open_scene(self, action: Action) -> None:
        factory = self.commands.get(f"scene:{action.data['name']}")
        if factory is None: raise RuntimeError(f"Scene is not registered: {action.data['name']}")
        factory(self)
    def _close_scene(self, action: Action) -> None:
        current = self.scene_stack.current
        if current is not None and getattr(current, "name", None) == action.data["name"]: self.pop_scene()

    def save_bundle(self, path, project_version: str = "1") -> None:
        bundle = SaveBundle(self.ENGINE_VERSION, project_version)
        bundle.state = {"runtime": self.state.variables, "extensions": self.game_state.serialize(), "scheduler": self.scheduler.serialize()}
        bundle.extensions = {name: system.serialize() for name, system in self.systems.items() if hasattr(system, "serialize")}
        bundle.rng = self.rng.serialize(); bundle.save(path)

    def load_bundle(self, path, project_version: str = "1") -> None:
        bundle = SaveBundle.load(path)
        if bundle.project_version != project_version: raise ValueError(f"project save version mismatch: {bundle.project_version} != {project_version}")
        self.state.variables = dict(bundle.state.get("runtime", {})); self.game_state.deserialize(bundle.state.get("extensions", {}))
        for name, payload in bundle.extensions.items():
            system = self.systems.get(name)
            if system is not None and hasattr(system, "deserialize"): system.deserialize(payload)
        self.rng.deserialize(bundle.rng); self.scheduler.deserialize(bundle.state.get("scheduler", {}))

    def advance(self) -> None:
        if not self.state.running: return
        import pygame
        now = pygame.time.get_ticks() / 1000.0
        if self.state.wait_until and now < self.state.wait_until: return
        self.state.wait_until = 0
        if self.state.paused_for_input:
            if self.state.dialogue: self.state.dialogue = None; self.state.paused_for_input = False
            return
        while self.state.index < len(self.state.story.actions) and self.state.running and not self.state.paused_for_input:
            action = self.state.story.actions[self.state.index]; self.state.index += 1; self.emit("before_action", {"action": action.kind, "data": action.data})
            if self.state.conditional_stack and not all(self.state.conditional_stack) and action.kind not in ("if", "else", "endif"): continue
            extension = self._extension_handlers.get(action.kind)
            if extension is not None: extension(action)
            else:
                handler = self._handlers.get(action.kind)
                if handler is None: raise RuntimeError(f"No runtime handler for action: {action.kind}")
                handler(action)
            self.emit("after_action", {"action": action.kind, "data": action.data})
            if action.kind in ("say", "choice", "end", "open_scene"): break

    def shutdown(self) -> None:
        self.emit("project.shutdown", {})
        for system in self.systems.values():
            close = getattr(system, "shutdown", None)
            if close is not None: close()
