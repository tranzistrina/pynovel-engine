from __future__ import annotations
from typing import Any
from vnengine.core.engine import Runtime as CoreRuntime
from vnengine.core.model import Action
from vnengine.core.rng import DeterministicRNG
from vnengine.core.save_bundle import SaveBundle
from vnengine.extensions.commands import CommandRegistry
from vnengine.extensions.events import EventBus
from vnengine.extensions.notifications import Notification, NotificationLog
from vnengine.extensions.scenes import SceneStack
from vnengine.extensions.scheduler import GameScheduler
from vnengine.extensions.state import StateRegistry
from vnengine.extensions.system import SystemRegistry
from vnengine.extensions.input import InputMap
from vnengine.map.movement import MovementController


class ExtensibleRuntime(CoreRuntime):
    """Core Runtime with opt-in project extension primitives."""

    ENGINE_VERSION = "0.38.0"

    def __init__(self, story, asset_root):
        super().__init__(story, asset_root)
        self.event_bus = EventBus(); self.systems = SystemRegistry(); self.commands = CommandRegistry()
        self.scene_stack = SceneStack(self); self.game_state = StateRegistry(); self.scheduler = GameScheduler(); self.rng = DeterministicRNG(0)
        self.notifications = NotificationLog()
        self.input_map = InputMap(); self._input_handlers: dict[str, list[Any]] = {}
        self.movement = None
        self._register_builtin_extension_actions(); self.emit("project.startup", {"title": story.title})

    def attach_movement(self, definition) -> MovementController:
        self.movement = MovementController(definition, self.emit)
        return self.movement

    def register_system(self, system) -> None: self.systems.register(system)
    def unregister_system(self, name: str) -> None: self.systems.unregister(name)
    def register_command(self, name: str, handler) -> None: self.commands.register(name, handler)
    def unregister_command(self, name: str) -> None: self.commands.unregister(name)
    def command_names(self) -> tuple[str, ...]: return self.commands.names()
    def subscribe(self, event_name: str, callback, priority: int = 0): return self.event_bus.subscribe(event_name, callback, priority)
    def unsubscribe(self, subscription) -> None: self.event_bus.unsubscribe(subscription)
    def emit(self, event_name: str, data: dict[str, Any] | None = None) -> bool: return self.event_bus.emit(event_name, data)
    def notify(self, title: str, body: str = "", *, severity: str = "info", icon: str | None = None, timestamp: int | None = None, action: str | None = None, notification_id: str | None = None) -> Notification:
        """Create a presentation notification and emit its creation event."""
        item = self.notifications.add(title, body, severity=severity, icon=icon, timestamp=self.scheduler.tick if timestamp is None else timestamp, action=action, notification_id=notification_id)
        self.emit("notification.created", item.serialize())
        return item
    def mark_notification_read(self, notification_id: str) -> bool:
        changed = self.notifications.mark_read(notification_id)
        if changed: self.emit("notification.read", {"id": notification_id})
        return changed
    def register_state_namespace(self, name: str, initial=None, version: int = 1) -> None: self.game_state.register(name, initial, version)
    def get_state(self, path: str, default=None): return self.game_state.get(path, default)
    def set_state(self, path: str, value) -> None: self.game_state.set(path, value)
    def push_scene(self, scene, **kwargs) -> None: self.scene_stack.push(scene, **kwargs)
    def pop_scene(self): return self.scene_stack.pop()
    def replace_scene(self, scene, **kwargs) -> None: self.scene_stack.replace(scene, **kwargs)
    def register_input_handler(self, action: str, handler) -> None: self._input_handlers.setdefault(action, []).append(handler)
    def unregister_input_handler(self, action: str, handler) -> None:
        handlers = self._input_handlers.get(action, [])
        self._input_handlers[action] = [item for item in handlers if item is not handler]
        if not self._input_handlers[action]: self._input_handlers.pop(action, None)

    def update(self, dt: float) -> None:
        super().update(dt)
        for system in self.systems.values(): system.update(dt, self.game_state)
        self.scene_stack.update(dt)
        if self.movement is not None: self.movement.update(dt)
        self.scheduler.advance_seconds(max(0.0, float(dt)), lambda item: self.emit(item.event, item.data))

    def dispatch_input(self, event: object) -> bool:
        if self.scene_stack.handle_input(event): return True
        handled = False
        for action in self._actions_for_event(event):
            payload = {"action": action, "event": event}
            self.emit("input.action", payload)
            for handler in tuple(self._input_handlers.get(action, ())):
                result = handler(event, self)
                handled = bool(result) or handled
        for system in self.systems.values():
            handled = bool(system.handle_event(event, self.game_state)) or handled
        return handled

    def _actions_for_event(self, event: object) -> tuple[str, ...]:
        event_type = getattr(event, "type", None)
        if event_type is None: return ()
        try:
            import pygame
            names = {pygame.KEYDOWN: "KEYDOWN", pygame.KEYUP: "KEYUP", pygame.MOUSEBUTTONDOWN: "MOUSEBUTTONDOWN", pygame.MOUSEBUTTONUP: "MOUSEBUTTONUP", pygame.MOUSEMOTION: "MOUSEMOTION"}
        except ImportError:
            names = {}
        event_name = names.get(event_type, str(event_type))
        code = getattr(event, "key", getattr(event, "button", ""))
        modifiers = int(getattr(event, "mod", 0))
        return self.input_map.actions_for(event_name, code, modifiers)

    def _register_builtin_extension_actions(self) -> None:
        self._extension_handlers = {"call_system": self._call_system, "emit": self._emit_action, "set_state": self._set_state, "open_scene": self._open_scene, "close_scene": self._close_scene}
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
        bundle.state = {"runtime": self.state.variables, "extensions": self.game_state.serialize(), "scheduler": self.scheduler.serialize(), "notifications": self.notifications.serialize(), "input_map": self.input_map.serialize()}
        bundle.extensions = {name: system.serialize() for name, system in self.systems.items() if hasattr(system, "serialize")}
        if self.movement is not None: bundle.extensions["__movement__"] = {k: _serialize_movement(v) for k, v in self.movement.active.items()}
        bundle.rng = self.rng.serialize(); bundle.save(path)

    def load_bundle(self, path, project_version: str = "1") -> None:
        bundle = SaveBundle.load(path)
        if bundle.project_version != project_version: raise ValueError(f"project save version mismatch: {bundle.project_version} != {project_version}")
        self.state.variables = dict(bundle.state.get("runtime", {})); self.game_state.deserialize(bundle.state.get("extensions", {})); self.notifications.deserialize(bundle.state.get("notifications", {})); self.input_map = InputMap.deserialize(bundle.state.get("input_map", []))
        for name, payload in bundle.extensions.items():
            if name == "__movement__":
                if self.movement is not None: self.movement.restore(payload)
                continue
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
            elif self.commands.dispatch(action.kind, self, action): pass
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


def _serialize_movement(movement):
    return {"route": list(movement.route.nodes), "position": [movement.position.x, movement.position.y], "segment": movement.segment, "progress": movement.progress, "speed": movement.speed, "paused": movement.paused, "cost": movement.route.cost}
