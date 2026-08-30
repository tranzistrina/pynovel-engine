from __future__ import annotations

from typing import Any

from vnengine.contracts import RuntimeContracts
from vnengine.core.engine import Runtime as CoreRuntime
from vnengine.core.rng import DeterministicRNG
from vnengine.core.save_bundle import SaveBundle
from vnengine.extensions.audio import AudioChannels
from vnengine.extensions.commands import CommandContext, CommandRegistry
from vnengine.extensions.events import EventSubscription
from vnengine.extensions.input import InputMap
from vnengine.extensions.notifications import NotificationLog
from vnengine.extensions.scenes import SceneStack
from vnengine.extensions.scheduler import GameScheduler
from vnengine.extensions.state import StateRegistry
from vnengine.extensions.system import SystemRegistry
from vnengine.map.movement import MovementController


class ExtensibleRuntime(CoreRuntime):
    """Compatibility runtime with a single runtime lifecycle and extension contract."""

    ENGINE_VERSION = "0.40.0"

    def __init__(self, story, asset_root):
        super().__init__(story, asset_root)
        self.contracts = RuntimeContracts()
        self.event_bus = self.contracts.events
        self.input_map = self.contracts.input_map
        self.systems = SystemRegistry(); self.commands = CommandRegistry(); self.scene_stack = SceneStack(self)
        self.game_state = StateRegistry(); self.scheduler = GameScheduler(); self.rng = DeterministicRNG(0); self.notifications = NotificationLog()
        self.audio = AudioChannels(asset_resolver=self.asset)
        self._input_handlers: dict[str, list[Any]] = {}; self.movement = None
        self._register_builtin_extension_actions(); self.emit("project.startup", {"title": story.title})

    # RuntimeProtocol -------------------------------------------------
    @property
    def running(self) -> bool:
        return bool(self.state.running)

    def start(self, **_: Any) -> None:
        self.new_game()
        self.state.running = True

    def handle_input(self, event: Any) -> bool:
        return self.dispatch_input(event)

    def render(self, target: Any) -> None:
        draw = getattr(self, "draw", None)
        if callable(draw): draw(target)

    def stop(self) -> None:
        self.state.running = False

    def save_state(self) -> dict[str, Any]:
        return {
            "runtime": dict(self.state.variables),
            "index": int(self.state.index),
            "history": list(self.state.history),
            "background": self.state.background_path,
            "extensions": self.game_state.serialize(),
            "scheduler": self.scheduler.serialize(),
            "notifications": self.notifications.serialize(),
            "audio": self.audio.serialize(),
            "input_map": self.input_map.serialize(),
            "systems": self.systems.serialize(),
            "rng": self.rng.serialize(),
        }

    def load_state(self, state: dict[str, Any]) -> None:
        self.state.variables = dict(state.get("runtime", {}))
        self.state.index = int(state.get("index", self.state.index))
        self.state.history = [tuple(item) for item in state.get("history", [])]
        self.state.background_path = state.get("background")
        self.game_state.deserialize(state.get("extensions", {}))
        self.notifications.deserialize(state.get("notifications", {}))
        self.audio.deserialize(state.get("audio", {}))
        self.input_map = InputMap.deserialize(state.get("input_map", []))
        self.contracts.input_map = self.input_map
        self.systems.deserialize(state.get("systems", {}))
        self.rng.deserialize(state.get("rng", {})); self.scheduler.deserialize(state.get("scheduler", {})); self.audio.restore_playback()

    # Extension API --------------------------------------------------
    def attach_movement(self, definition): self.movement = MovementController(definition, self.emit); return self.movement
    def register_system(self, system): self.systems.register(system)
    def unregister_system(self, name): self.systems.unregister(name)
    def register_command(self, name, handler): self.commands.register(name, handler)
    def unregister_command(self, name): self.commands.unregister(name)
    def command_names(self): return self.commands.names()
    def subscribe(self, event_name, callback, priority=0) -> EventSubscription: return self.contracts.subscribe(event_name, callback, priority)
    def unsubscribe(self, subscription): self.contracts.unsubscribe(subscription)
    def emit(self, event_name, data=None): return self.contracts.emit(event_name, data)

    def notify(self, title, body="", **kwargs):
        item = self.notifications.add(title, body, **kwargs); self.emit("notification.created", item.serialize()); return item

    def mark_notification_read(self, notification_id):
        changed = self.notifications.mark_read(notification_id)
        if changed: self.emit("notification.read", {"id": notification_id})
        return changed

    def register_state_namespace(self, name, initial=None, version=1): self.game_state.register(name, initial, version)
    def get_state(self, path, default=None): return self.game_state.get(path, default)
    def set_state(self, path, value): self.game_state.set(path, value)
    def push_scene(self, scene, **kwargs): self.scene_stack.push(scene, **kwargs)
    def pop_scene(self): return self.scene_stack.pop()
    def replace_scene(self, scene, **kwargs): return self.scene_stack.replace(scene, **kwargs)
    def register_input_handler(self, action, handler): self._input_handlers.setdefault(str(action), []).append(handler)

    def unregister_input_handler(self, action, handler):
        handlers = [item for item in self._input_handlers.get(action, []) if item is not handler]
        if handlers: self._input_handlers[action] = handlers
        else: self._input_handlers.pop(action, None)

    def bind_input(self, action, event_type, code, modifiers=0): return self.contracts.input_map.bind(action, event_type, code, modifiers)

    def update(self, dt):
        super().update(dt)
        for system in self.systems.values(): system.update(dt, self.game_state)
        self.scene_stack.update(dt)
        if self.movement is not None: self.movement.update(dt)
        self.scheduler.advance_seconds(max(0.0, float(dt)), lambda item: self.emit(item.event, item.data))

    def dispatch_input(self, event):
        handled = self.scene_stack.handle_input(event)
        event_type, code, modifiers = self._normalize_input_event(event)
        for action in self.input_map.actions_for(event_type, code, modifiers):
            payload = {"action": action, "event": event}
            self.emit("input.action", payload); self.emit(f"input.action.{action}", payload)
            for handler in tuple(self._input_handlers.get(action, ())): handled = bool(handler(event, self)) or handled
        for system in self.systems.values():
            handler = getattr(system, "handle_event", None)
            if callable(handler): handled = bool(handler(event, self.game_state)) or handled
        return handled

    @staticmethod
    def _normalize_input_event(event):
        event_type = getattr(event, "type", None)
        if event_type is None: return "", "", 0
        try:
            import pygame
            names = {pygame.KEYDOWN: "KEYDOWN", pygame.KEYUP: "KEYUP", pygame.MOUSEBUTTONDOWN: "MOUSEBUTTONDOWN", pygame.MOUSEBUTTONUP: "MOUSEBUTTONUP", pygame.MOUSEMOTION: "MOUSEMOTION"}
        except ImportError: names = {}
        return names.get(event_type, str(event_type)), getattr(event, "key", getattr(event, "button", "")), int(getattr(event, "mod", 0))

    def _register_builtin_extension_actions(self): self._extension_handlers = {"call_system": self._call_system, "emit": self._emit_action, "set_state": self._set_state, "open_scene": self._open_scene, "close_scene": self._close_scene}
    def _call_system(self, action):
        system = self.systems.get(action.data["system"])
        if system is None: raise RuntimeError(f"Unknown game system: {action.data['system']}")
        method_name = str(action.data["method"]); method = getattr(system, method_name, None)
        if not callable(method) or method_name.startswith("_"): raise RuntimeError(f"System method is not callable: {method_name}")
        method(*action.data.get("args", []))
    def _emit_action(self, action): self.emit(action.data["event"], {"args": list(action.data.get("args", []))})
    def _set_state(self, action):
        from vnengine.core.expressions import evaluate
        value = evaluate(action.data["expression"], self.state.variables); self.set_state(action.data["path"], value); self.emit("state.changed", {"path": action.data["path"], "value": value})
    def _open_scene(self, action):
        handler = self.commands.get(f"scene:{action.data['name']}")
        if handler is None: raise RuntimeError(f"Scene is not registered: {action.data['name']}")
        handler(CommandContext(self, action))
    def _close_scene(self, action):
        current = self.scene_stack.current
        if current is not None and getattr(current, "name", None) == action.data["name"]: self.pop_scene()

    def save_bundle(self, path, project_version="1", metadata=None):
        bundle = SaveBundle(self.ENGINE_VERSION, project_version)
        bundle.state = self.save_state(); bundle.metadata = dict(metadata or {}); bundle.extensions = self.systems.serialize(); bundle.rng = self.rng.serialize(); bundle.save(path)

    def load_bundle(self, path, project_version="1"):
        bundle = SaveBundle.load(path)
        if bundle.project_version != project_version: raise ValueError(f"project save version mismatch: {bundle.project_version} != {project_version}")
        state = dict(bundle.state); state.setdefault("systems", bundle.extensions); state.setdefault("rng", bundle.rng); self.load_state(state)

    def shutdown(self):
        self.emit("project.shutdown", {})
        for system in self.systems.values():
            close = getattr(system, "shutdown", None)
            if callable(close): close()
