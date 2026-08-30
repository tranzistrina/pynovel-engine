from __future__ import annotations

from dataclasses import dataclass, field
from contextlib import contextmanager
from time import perf_counter
from typing import Any, Iterator


@dataclass(slots=True)
class ProfileSample:
    name: str
    elapsed: float
    calls: int = 1


class Profiler:
    """Low-overhead profiler for deterministic/headless and development runs."""

    def __init__(self, enabled: bool = False) -> None:
        self.enabled = bool(enabled)
        self._samples: dict[str, ProfileSample] = {}

    def reset(self) -> None:
        self._samples.clear()

    @contextmanager
    def measure(self, name: str) -> Iterator[None]:
        if not self.enabled:
            yield
            return
        start = perf_counter()
        try:
            yield
        finally:
            elapsed = perf_counter() - start
            sample = self._samples.get(name)
            if sample is None:
                self._samples[name] = ProfileSample(name, elapsed)
            else:
                sample.elapsed += elapsed
                sample.calls += 1

    def record(self, name: str, elapsed: float) -> None:
        if not self.enabled:
            return
        sample = self._samples.get(name)
        if sample is None:
            self._samples[name] = ProfileSample(name, float(elapsed))
        else:
            sample.elapsed += float(elapsed)
            sample.calls += 1

    def snapshot(self) -> dict[str, dict[str, Any]]:
        return {
            name: {
                "elapsed": sample.elapsed,
                "calls": sample.calls,
                "average": sample.elapsed / sample.calls if sample.calls else 0.0,
            }
            for name, sample in sorted(self._samples.items())
        }


@dataclass(slots=True)
class FixedTimestep:
    """Accumulator-based fixed-step scheduler with a bounded catch-up loop."""

    step: float = 1.0 / 60.0
    max_steps: int = 8
    accumulator: float = 0.0

    def __post_init__(self) -> None:
        if self.step <= 0.0:
            raise ValueError("fixed timestep must be positive")
        if self.max_steps <= 0:
            raise ValueError("max_steps must be positive")

    def reset(self) -> None:
        self.accumulator = 0.0

    def advance(self, dt: float) -> int:
        self.accumulator += max(0.0, float(dt))
        steps = min(int(self.accumulator / self.step), self.max_steps)
        self.accumulator -= steps * self.step
        if steps >= self.max_steps:
            self.accumulator = min(self.accumulator, self.step)
        return steps


class FrameCache:
    """Small bounded cache for runtime objects and decoded assets."""

    def __init__(self, capacity: int = 256) -> None:
        if capacity <= 0:
            raise ValueError("cache capacity must be positive")
        self.capacity = int(capacity)
        self._values: dict[str, Any] = {}
        self._order: list[str] = []

    def get(self, key: str, default: Any = None) -> Any:
        if key not in self._values:
            return default
        self._touch(key)
        return self._values[key]

    def put(self, key: str, value: Any) -> Any:
        if key in self._values:
            self._values[key] = value
            self._touch(key)
            return value
        self._values[key] = value
        self._order.append(key)
        while len(self._order) > self.capacity:
            oldest = self._order.pop(0)
            self._values.pop(oldest, None)
        return value

    def clear(self) -> None:
        self._values.clear()
        self._order.clear()

    def __len__(self) -> int:
        return len(self._values)

    def _touch(self, key: str) -> None:
        try:
            self._order.remove(key)
        except ValueError:
            pass
        self._order.append(key)


__all__ = ["ProfileSample", "Profiler", "FixedTimestep", "FrameCache"]
