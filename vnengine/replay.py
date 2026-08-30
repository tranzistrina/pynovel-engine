from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
from typing import Any, Iterable


@dataclass(frozen=True, slots=True)
class ReplayFrame:
    dt: float
    events: tuple[Any, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {"dt": self.dt, "events": list(self.events)}


@dataclass(slots=True)
class ReplaySession:
    """Deterministic input/timestep recording and playback for runtime tools."""

    frames: list[ReplayFrame] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def record(self, dt: float, events: Iterable[Any] = ()) -> ReplayFrame:
        frame = ReplayFrame(float(dt), tuple(events))
        self.frames.append(frame)
        return frame

    def clear(self) -> None:
        self.frames.clear()

    def to_dict(self) -> dict[str, Any]:
        return {"version": 1, "metadata": dict(self.metadata), "frames": [frame.to_dict() for frame in self.frames]}

    def digest(self) -> str:
        payload = json.dumps(self.to_dict(), ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "ReplaySession":
        if not isinstance(payload, dict):
            raise ValueError("Replay payload must be an object")
        if int(payload.get("version", 1)) != 1:
            raise ValueError(f"Unsupported replay version: {payload.get('version')}")
        session = cls(metadata=dict(payload.get("metadata", {})))
        for index, raw in enumerate(payload.get("frames", [])):
            if not isinstance(raw, dict):
                raise ValueError(f"Invalid replay frame at index {index}")
            session.record(float(raw.get("dt", 0.0)), raw.get("events", ()))
        return session


class ReplayPlayer:
    def __init__(self, session: ReplaySession) -> None:
        self.session = session
        self.index = 0

    @property
    def finished(self) -> bool:
        return self.index >= len(self.session.frames)

    def reset(self) -> None:
        self.index = 0

    def next_frame(self) -> ReplayFrame | None:
        if self.finished:
            return None
        frame = self.session.frames[self.index]
        self.index += 1
        return frame

    def remaining(self) -> int:
        return max(0, len(self.session.frames) - self.index)


__all__ = ["ReplayFrame", "ReplaySession", "ReplayPlayer"]
