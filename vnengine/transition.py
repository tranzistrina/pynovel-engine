from __future__ import annotations
from dataclasses import dataclass


@dataclass(slots=True)
class SceneTransition:
    """Time-based transition state independent of the renderer."""
    kind: str = "instant"
    duration: float = 0.0
    elapsed: float = 0.0

    @property
    def progress(self) -> float:
        if self.duration <= 0: return 1.0
        return min(1.0, max(0.0, self.elapsed / self.duration))

    @property
    def finished(self) -> bool: return self.progress >= 1.0

    def update(self, dt: float) -> float:
        self.elapsed = min(max(0.0, self.elapsed + max(0.0, dt)), max(0.0, self.duration))
        return self.progress


class TransitionManager:
    """Creates and advances scene transitions; rendering remains a frontend concern."""
    def __init__(self) -> None: self.current: SceneTransition | None = None

    def start(self, kind: str = "instant", duration: float = 0.0) -> SceneTransition:
        if duration < 0: raise ValueError("Transition duration cannot be negative")
        self.current = SceneTransition(kind=kind, duration=duration)
        return self.current

    def update(self, dt: float) -> float:
        if self.current is None: return 1.0
        progress = self.current.update(dt)
        if self.current.finished: self.current = None
        return progress

    @property
    def active(self) -> bool: return self.current is not None
