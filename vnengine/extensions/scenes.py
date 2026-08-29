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


class SceneStack:
    """Reusable non-linear scene stack for overlays and modal game scenes."""

    def __init__(self, context: Any = None) -> None:
        self.context = context
        self._entries: list[SceneEntry] = []

    def __len__(self) -> int:
        return len(self._entries)

    @property
    def current(self) -> Scene | None:
        return self._entries[-1].scene if self._entries else None

    def push(self, scene: Scene, *, pause_underlying: bool = True, input_focus: bool = True) -> None:
        if self.current is not None and hasattr(self.current, "pause") and pause_underlying:
            self.current.pause()
        self._entries.append(SceneEntry(scene, pause_underlying, input_focus))
        scene.enter(self.context)

    def pop(self) -> Scene | None:
        if not self._entries:
            return None
        entry = self._entries.pop()
        entry.scene.exit()
        if self.current is not None and entry.pause_underlying and hasattr(self.current, "resume"):
            self.current.resume()
        return entry.scene

    def replace(self, scene: Scene, *, pause_underlying: bool = True, input_focus: bool = True) -> None:
        if self._entries:
            entry = self._entries.pop()
            entry.scene.exit()
        self._entries.append(SceneEntry(scene, pause_underlying, input_focus))
        scene.enter(self.context)

    def update(self, dt: float) -> None:
        for index, entry in enumerate(self._entries):
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
