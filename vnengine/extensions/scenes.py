from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


class Scene(Protocol):
    name: str
    def enter(self, context: Any) -> None: ...
    def exit(self) -> None: ...
    def update(self, dt: float) -> None: ...
    def handle_input(self, event: object) -> bool: ...
    def draw(self, surface: Any) -> None: ...


@dataclass(slots=True)
class SceneEntry:
    scene: Scene
    pause_underlying: bool = True
    input_focus: bool = True
    paused: bool = False


class SceneStack:
    """Reusable scene stack with explicit, rollback-safe lifecycle semantics."""

    def __init__(self, context: Any = None) -> None:
        self.context = context
        self._entries: list[SceneEntry] = []

    def __len__(self) -> int:
        return len(self._entries)

    @property
    def current(self) -> Scene | None:
        return self._entries[-1].scene if self._entries else None

    def push(self, scene: Scene, *, pause_underlying: bool = True, input_focus: bool = True) -> None:
        previous = self._entries[-1] if self._entries else None
        if previous is not None and pause_underlying:
            self._pause(previous)
        entry = SceneEntry(scene, pause_underlying, input_focus)
        try:
            scene.enter(self.context)
        except Exception:
            if previous is not None and previous.paused:
                self._resume(previous)
            raise
        self._entries.append(entry)

    def pop(self) -> Scene | None:
        if not self._entries:
            return None
        entry = self._entries[-1]
        entry.scene.exit()
        self._entries.pop()
        previous = self._entries[-1] if self._entries else None
        if previous is not None and entry.pause_underlying:
            self._resume(previous)
        return entry.scene

    def replace(self, scene: Scene, *, pause_underlying: bool = True, input_focus: bool = True) -> None:
        previous = self._entries.pop() if self._entries else None
        if previous is not None:
            previous.scene.exit()
        entry = SceneEntry(scene, pause_underlying, input_focus)
        try:
            scene.enter(self.context)
        except Exception:
            if previous is not None:
                self._entries.append(previous)
            raise
        self._entries.append(entry)

    def update(self, dt: float) -> None:
        for index, entry in enumerate(tuple(self._entries)):
            if entry.pause_underlying and index < len(self._entries) - 1:
                continue
            entry.scene.update(dt)

    def handle_input(self, event: object) -> bool:
        for entry in reversed(self._entries):
            if not entry.input_focus:
                continue
            if entry.scene.handle_input(event):
                return True
            if entry.pause_underlying:
                return False
        return False

    def draw(self, surface: Any) -> None:
        for entry in self._entries:
            entry.scene.draw(surface)

    @staticmethod
    def _pause(entry: SceneEntry) -> None:
        callback = getattr(entry.scene, "pause", None)
        if callable(callback):
            callback()
        entry.paused = True

    @staticmethod
    def _resume(entry: SceneEntry) -> None:
        if not entry.paused:
            return
        callback = getattr(entry.scene, "resume", None)
        if callable(callback):
            callback()
        entry.paused = False

    def ids(self) -> tuple[str, ...]:
        return tuple(getattr(entry.scene, "name", "") for entry in self._entries)
