from __future__ import annotations
from typing import Any, Callable
from .project_runtime import ProjectRuntime


class ProjectRunner:
    """Frontend-neutral application loop for a ProjectRuntime."""
    def __init__(self, runtime: ProjectRuntime, *, poll_events: Callable[[], Any] | None = None, present: Callable[[Any], None] | None = None, target: Any = None, clock: Callable[[], float] | None = None):
        self.runtime = runtime; self.poll_events = poll_events or (lambda: ()); self.present = present or (lambda _: None)
        self.target = target; self.clock = clock; self.running = False

    def step(self, dt: float) -> None:
        for event in self.poll_events():
            if getattr(event, "quit", False): self.running = False; continue
            self.runtime.handle_input(event)
        self.runtime.update(dt); self.runtime.render(self.target); self.present(self.target)

    def run(self, *, max_frames: int | None = None) -> None:
        self.runtime.start(); self.running = True; frames = 0
        try:
            while self.running:
                dt = float(self.clock()) if self.clock is not None else 0.0
                self.step(max(0.0, dt)); frames += 1
                if max_frames is not None and frames >= max_frames: self.running = False
        finally:
            self.runtime.stop()
