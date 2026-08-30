from __future__ import annotations

from typing import Any

from .components import ComponentSystem


class TransformSystem(ComponentSystem):
    """Applies declarative velocity to transform components."""

    def __init__(self, name="movement", *, settings=None):
        settings = settings or {}
        super().__init__(name, requires=("transform", "velocity"))
        self.scale = float(settings.get("scale", 1.0))

    def process(self, entity: Any, dt: float, state: Any) -> None:
        transform = entity.get_component("transform", {})
        velocity = entity.get_component("velocity", {})
        if not isinstance(transform, dict) or not isinstance(velocity, dict):
            return
        transform["x"] = float(transform.get("x", 0.0)) + float(velocity.get("x", 0.0)) * dt * self.scale
        transform["y"] = float(transform.get("y", 0.0)) + float(velocity.get("y", 0.0)) * dt * self.scale


class StateSystem(ComponentSystem):
    """Ticks a declarative timer in state components."""

    def __init__(self, name="state", *, settings=None):
        super().__init__(name, requires=("state",))
        self.timer_key = str((settings or {}).get("timer_key", "time"))

    def process(self, entity: Any, dt: float, state: Any) -> None:
        payload = entity.get_component("state", {})
        if isinstance(payload, dict):
            payload[self.timer_key] = float(payload.get(self.timer_key, 0.0)) + dt


class InputSystem(ComponentSystem):
    """Receives input events for systems that expose on_event()."""

    def __init__(self, name="input", *, settings=None):
        super().__init__(name, requires=())
        self.last_event: Any = None

    def on_event(self, event: str, data: Any = None) -> None:
        self.last_event = {"event": event, "data": data}


BUILTIN_SYSTEM_FACTORIES = {
    "movement": lambda spec: TransformSystem(spec.name, settings=spec.settings),
    "state": lambda spec: StateSystem(spec.name, settings=spec.settings),
    "input": lambda spec: InputSystem(spec.name, settings=spec.settings),
}


__all__ = ["TransformSystem", "StateSystem", "InputSystem", "BUILTIN_SYSTEM_FACTORIES"]
