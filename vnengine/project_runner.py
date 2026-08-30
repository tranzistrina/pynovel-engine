from __future__ import annotations
from typing import Any, Callable
from .runtime_protocol import RuntimeProtocol, require_runtime


class ProjectRunner:
    """Frontend-neutral application loop for any RuntimeProtocol implementation."""
    def __init__(self, runtime: RuntimeProtocol, *, poll_events: Callable[[], Any] | None = None, present: Callable[[Any], None] | None = None, target: Any = None, clock: Callable[[], float] | None = None):
        self.runtime = require_runtime(runtime)
        self.poll_events = poll_events or (lambda: ())
        self.present = present or (lambda _: None)
        self.target = target
        self.clock = clock
        self.running = False

    @staticmethod
    def _is_quit(event: Any) -> bool:
        if getattr(event, "quit", False): return True
        event_type = getattr(event, "type", None)
        return event_type == "QUIT" or getattr(event_type, "name", None) == "QUIT"

    def step(self, dt: float) -> None:
        if not self.running:
            self.running = bool(self.runtime.running)
        for event in self.poll_events():
            if self._is_quit(event):
                self.running = False
                continue
            self.runtime.handle_input(event)
        self.runtime.update(max(0.0, float(dt)))
        self.runtime.render(self.target)
        self.present(self.target)
        if not self.runtime.running:
            self.running = False

    def run(self, *, max_frames: int | None = None) -> None:
        self.runtime.start()
        self.running = True
        frames = 0
        try:
            while self.running and self.runtime.running:
                dt = float(self.clock()) if self.clock is not None else 0.0
                self.step(dt)
                frames += 1
                if max_frames is not None and frames >= max_frames:
                    self.running = False
        finally:
            self.runtime.stop()
            self.running = False
