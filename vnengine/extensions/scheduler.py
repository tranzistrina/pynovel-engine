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
        self._fractional_ticks = 0.0
        self._order = 0
        self._queue: list[tuple[int, int, ScheduledEvent]] = []

    @property
    def day(self) -> int:
        return self.tick // self.tick_rate + 1

    def schedule(self, after: int, event: str, data: dict[str, Any] | None = None) -> ScheduledEvent:
        if after < 0 or not event:
            raise ValueError("after must be non-negative and event must not be empty")
        item = ScheduledEvent(self.tick + int(after), self._order, event, dict(data or {}))
        self._order += 1
        heapq.heappush(self._queue, (item.due, item.order, item))
        return item

    def schedule_at(self, tick: int, event: str, data: dict[str, Any] | None = None) -> ScheduledEvent:
        tick = int(tick)
        if tick < self.tick:
            raise ValueError("tick cannot be earlier than the current clock")
        return self.schedule(tick - self.tick, event, data)

    def cancel(self, item: ScheduledEvent) -> bool:
        for index, (_, _, queued) in enumerate(self._queue):
            if queued == item:
                self._queue.pop(index)
                heapq.heapify(self._queue)
                return True
        return False

    def advance_seconds(self, seconds: float, dispatch: Callable[[ScheduledEvent], None] | None = None) -> tuple[ScheduledEvent, ...]:
        """Advance using wall-clock delta as input while preserving deterministic ticks."""
        if seconds < 0:
            raise ValueError("seconds must be non-negative")
        return self.advance(seconds * self.tick_rate, dispatch)

    def advance(self, ticks: float = 1, dispatch: Callable[[ScheduledEvent], None] | None = None) -> tuple[ScheduledEvent, ...]:
        if ticks < 0:
            raise ValueError("ticks must be non-negative")
        if self.paused or ticks == 0:
            return ()
        scaled = ticks * self.time_scale + self._fractional_ticks
        whole = int(scaled)
        self._fractional_ticks = scaled - whole
        if whole <= 0:
            return ()
        self.tick += whole
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
            "fractional_ticks": self._fractional_ticks,
            "order": self._order,
            "queue": [asdict(item) for _, _, item in sorted(self._queue)],
        }

    def deserialize(self, payload: dict[str, Any]) -> None:
        self.tick_rate = int(payload.get("tick_rate", self.tick_rate))
        if self.tick_rate <= 0:
            raise ValueError("tick_rate must be positive")
        self.tick = int(payload.get("tick", 0))
        self.paused = bool(payload.get("paused", False))
        self.time_scale = float(payload.get("time_scale", 1.0))
        self._fractional_ticks = float(payload.get("fractional_ticks", 0.0))
        self._order = int(payload.get("order", 0))
        self._queue.clear()
        for raw in payload.get("queue", []):
            item = ScheduledEvent(int(raw["due"]), int(raw["order"]), raw["event"], dict(raw.get("data", {})))
            heapq.heappush(self._queue, (item.due, item.order, item))
