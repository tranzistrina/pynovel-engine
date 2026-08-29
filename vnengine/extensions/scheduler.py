from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any, Callable
import heapq


@dataclass(frozen=True, slots=True)
class ScheduledEvent:
    due: int
    order: int
    event: str
    data: dict[str, Any]


class GameScheduler:
    """Deterministic simulation clock measured in integer ticks."""

    def __init__(self, tick_rate: int = 1) -> None:
        if tick_rate <= 0:
            raise ValueError("tick_rate must be positive")
        self.tick_rate = int(tick_rate)
        self.tick = 0
        self.paused = False
        self.time_scale = 1.0
        self._order = 0
        self._queue: list[tuple[int, int, ScheduledEvent]] = []

    def schedule(self, after: int, event: str, data: dict[str, Any] | None = None) -> ScheduledEvent:
        if after < 0 or not event:
            raise ValueError("after must be non-negative and event must not be empty")
        item = ScheduledEvent(self.tick + int(after), self._order, event, dict(data or {}))
        self._order += 1
        heapq.heappush(self._queue, (item.due, item.order, item))
        return item

    def advance(self, ticks: int = 1, dispatch: Callable[[ScheduledEvent], None] | None = None) -> tuple[ScheduledEvent, ...]:
        if ticks < 0:
            raise ValueError("ticks must be non-negative")
        if self.paused:
            return ()
        self.tick += int(ticks * self.time_scale)
        fired: list[ScheduledEvent] = []
        while self._queue and self._queue[0][0] <= self.tick:
            item = heapq.heappop(self._queue)[2]
            fired.append(item)
            if dispatch is not None:
                dispatch(item)
        return tuple(fired)

    def serialize(self) -> dict[str, Any]:
        return {
            "tick_rate": self.tick_rate,
            "tick": self.tick,
            "paused": self.paused,
            "time_scale": self.time_scale,
            "order": self._order,
            "queue": [asdict(item) for _, _, item in sorted(self._queue)],
        }

    def deserialize(self, payload: dict[str, Any]) -> None:
        self.tick_rate = int(payload.get("tick_rate", self.tick_rate))
        self.tick = int(payload.get("tick", 0))
        self.paused = bool(payload.get("paused", False))
        self.time_scale = float(payload.get("time_scale", 1.0))
        self._order = int(payload.get("order", 0))
        self._queue.clear()
        for raw in payload.get("queue", []):
            item = ScheduledEvent(int(raw["due"]), int(raw["order"]), raw["event"], dict(raw.get("data", {})))
            heapq.heappush(self._queue, (item.due, item.order, item))
