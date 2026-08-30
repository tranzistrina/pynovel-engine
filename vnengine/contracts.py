from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from .extensions.events import Event, EventBus, EventSubscription
from .extensions.input import InputMap


@dataclass(frozen=True, slots=True)
class InputAction:
    name: str
    event: Any


class RuntimeContracts:
    """Shared input/event contract used by all runtime frontends."""

    def __init__(self, *, input_map: InputMap | None = None, events: EventBus | None = None) -> None:
        self.input_map = input_map or InputMap()
        self.events = events or EventBus()

    def bind(self, action: str, event_type: str, code: int | str, modifiers: int = 0) -> None:
        self.input_map.bind(action, event_type, code, modifiers)

    def actions_for(self, event_type: str | int, code: int | str, modifiers: int = 0) -> tuple[InputAction, ...]:
        return tuple(InputAction(name, None) for name in self.input_map.actions_for(event_type, code, modifiers))

    def dispatch(self, event: Any, *, event_type: str | int, code: int | str, modifiers: int = 0) -> bool:
        handled = False
        for action in self.input_map.actions_for(event_type, code, modifiers):
            handled = self.events.emit("input.action", {"action": action, "event": event}) or handled
            handled = self.events.emit(f"input.action.{action}", {"action": action, "event": event}) or handled
        return handled

    def subscribe(self, event_name: str, callback: Callable[[Event], bool | None], priority: int = 0) -> EventSubscription:
        return self.events.subscribe(event_name, callback, priority)

    def unsubscribe(self, subscription: EventSubscription) -> None:
        self.events.unsubscribe(subscription)

    def emit(self, name: str, data: dict[str, Any] | None = None) -> bool:
        return self.events.emit(name, data)
