from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Callable


Handler = Callable[[Any], Any]


@dataclass(frozen=True, slots=True)
class EventSubscription:
    event: str
    token: int


class EventBus:
    """Deterministic publish/subscribe bus with explicit subscription tokens."""

    def __init__(self) -> None:
        self._handlers: dict[str, list[tuple[int, Handler]]] = defaultdict(list)
        self._next_token = 1
        self._queue: list[tuple[str, Any]] = []

    def subscribe(self, event: str, handler: Handler) -> EventSubscription:
        name = str(event).strip()
        if not name:
            raise ValueError("Event name must not be empty")
        token = self._next_token
        self._next_token += 1
        self._handlers[name].append((token, handler))
        return EventSubscription(name, token)

    def unsubscribe(self, subscription: EventSubscription | int) -> bool:
        token = subscription.token if isinstance(subscription, EventSubscription) else int(subscription)
        for event, handlers in self._handlers.items():
            for index, (candidate, _) in enumerate(handlers):
                if candidate == token:
                    handlers.pop(index)
                    if not handlers:
                        self._handlers.pop(event, None)
                    return True
        return False

    def emit(self, event: str, data: Any = None) -> int:
        name = str(event)
        handlers = tuple(self._handlers.get(name, ()))
        for _, handler in handlers:
            handler(data)
        return len(handlers)

    def queue(self, event: str, data: Any = None) -> None:
        self._queue.append((str(event), data))

    def flush(self) -> int:
        delivered = 0
        pending, self._queue = self._queue, []
        for event, data in pending:
            delivered += self.emit(event, data)
        return delivered

    def clear(self) -> None:
        self._handlers.clear()
        self._queue.clear()

    def listeners(self, event: str | None = None) -> int:
        if event is not None:
            return len(self._handlers.get(str(event), ()))
        return sum(len(items) for items in self._handlers.values())


__all__ = ["EventBus", "EventSubscription"]
