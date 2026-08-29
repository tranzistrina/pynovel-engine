from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True, slots=True)
class EventSubscription:
    event_name: str
    token: int


@dataclass(frozen=True, slots=True)
class Event:
    name: str
    data: dict[str, Any]


@dataclass(slots=True)
class _Listener:
    token: int
    priority: int
    order: int
    callback: Callable[[Event], bool | None]


class EventBus:
    def __init__(self) -> None:
        self._listeners: dict[str, list[_Listener]] = {}
        self._next_token = 1
        self._order = 0

    def subscribe(self, event_name: str, callback: Callable[[Event], bool | None], priority: int = 0) -> EventSubscription:
        if not event_name:
            raise ValueError("event_name must not be empty")
        listener = _Listener(self._next_token, int(priority), self._order, callback)
        self._next_token += 1
        self._order += 1
        self._listeners.setdefault(event_name, []).append(listener)
        self._listeners[event_name].sort(key=lambda item: (-item.priority, item.order))
        return EventSubscription(event_name, listener.token)

    def unsubscribe(self, subscription: EventSubscription) -> None:
        listeners = self._listeners.get(subscription.event_name, [])
        self._listeners[subscription.event_name] = [item for item in listeners if item.token != subscription.token]
        if not self._listeners[subscription.event_name]:
            self._listeners.pop(subscription.event_name, None)

    def emit(self, event_name: str, data: dict[str, Any] | None = None) -> bool:
        event = Event(event_name, dict(data or {}))
        handled = False
        for listener in tuple(self._listeners.get(event_name, ())):
            if listener.callback(event):
                handled = True
        return handled

    def clear(self) -> None:
        self._listeners.clear()
