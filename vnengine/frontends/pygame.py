from __future__ import annotations

from typing import Any
from vnengine.project_runner import ProjectRunner


class PygameFrontend:
    """Thin pygame adapter. Imports pygame lazily so the core stays optional."""
    def __init__(self, *, width: int = 1280, height: int = 720, title: str = "PyNovel Engine", fps: int = 60):
        self.width = width; self.height = height; self.title = title; self.fps = fps
        self._pygame: Any = None; self.screen: Any = None; self.clock: Any = None

    def open(self) -> None:
        import pygame
        self._pygame = pygame; pygame.init(); self.screen = pygame.display.set_mode((self.width, self.height)); pygame.display.set_caption(self.title); self.clock = pygame.time.Clock()

    def events(self):
        if self._pygame is None: return ()
        return self._pygame.event.get()

    def tick(self) -> float:
        if self.clock is None: return 0.0
        return self.clock.tick(self.fps) / 1000.0

    def present(self, target: Any) -> None:
        if self._pygame is not None: self._pygame.display.flip()

    def close(self) -> None:
        if self._pygame is not None: self._pygame.quit(); self._pygame = None

    def run(self, runtime, *, max_frames: int | None = None) -> None:
        self.open()
        runner = ProjectRunner(runtime, poll_events=self.events, present=self.present, target=self.screen, clock=self.tick)
        try: runner.run(max_frames=max_frames)
        finally: self.close()
