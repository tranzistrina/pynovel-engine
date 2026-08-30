from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Iterable

from .project_runtime import ProjectRuntime
from .project_runner import ProjectRunner


@dataclass(slots=True)
class FrameResult:
    frame: int
    dt: float
    scene: str | None
    state: dict[str, Any]
    running: bool


class HeadlessFrontend:
    """Deterministic frontend adapter for CI, tests and AI agents."""
    def __init__(self, *, events: Iterable[Any] = ()) -> None:
        self._events = list(events)
        self.frames: list[Any] = []
        self.screen = None

    def open(self) -> None: pass
    def close(self) -> None: pass
    def events(self) -> list[Any]:
        events, self._events = self._events, []
        return events
    def present(self, target: Any = None) -> None: self.frames.append(target)
    def tick(self) -> float: return 1.0 / 60.0


class HeadlessHarness:
    """Run projects without a window and expose reproducible runtime snapshots."""
    def __init__(self, project: str, *, runtime_factory: Callable[..., ProjectRuntime] = ProjectRuntime):
        self.frontend = HeadlessFrontend()
        self.runtime = runtime_factory(project, frontend=self.frontend)
        self.runner = ProjectRunner(self.runtime, poll_events=self.frontend.events, present=self.frontend.present, target=None, clock=self.frontend.tick)

    def start(self) -> dict[str, Any]:
        self.runtime.start(); self.runner.running = True
        return self.snapshot()

    def step(self, dt: float = 1.0 / 60.0, events: Iterable[Any] = ()) -> FrameResult:
        self.frontend._events.extend(events)
        self.runner.running = self.runtime.running
        self.runner.step(dt)
        return self.snapshot()

    def run(self, frames: int, *, dt: float = 1.0 / 60.0) -> list[FrameResult]:
        if not self.runtime.running: self.start()
        results = []
        for _ in range(max(0, int(frames))):
            if not self.runner.running: break
            results.append(self.step(dt))
        return results

    def snapshot(self) -> FrameResult:
        return FrameResult(len(self.frontend.frames), 0.0, self.runtime.scene_id, self.runtime.save_state(), self.runtime.running)

    def stop(self) -> None: self.runtime.stop(); self.runner.running = False
