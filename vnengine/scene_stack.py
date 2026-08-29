from __future__ import annotations
from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class SceneEntry:
    scene_id: str
    scene: Any
    paused: bool = False


class SceneStack:
    """Stack of active runtime scenes for overlays, menus and temporary modes."""
    def __init__(self) -> None: self._stack: list[SceneEntry] = []

    def push(self, scene_id: str, scene: Any) -> Any:
        if self._stack: self._stack[-1].paused = True
        self._stack.append(SceneEntry(scene_id, scene)); return scene

    def pop(self) -> Any:
        if not self._stack: raise IndexError("Cannot pop an empty scene stack")
        entry = self._stack.pop()
        if self._stack: self._stack[-1].paused = False
        return entry.scene

    @property
    def current(self) -> Any | None: return self._stack[-1].scene if self._stack else None
    @property
    def current_id(self) -> str | None: return self._stack[-1].scene_id if self._stack else None
    def ids(self) -> tuple[str, ...]: return tuple(entry.scene_id for entry in self._stack)
    def is_paused(self, scene_id: str) -> bool: return next((e.paused for e in self._stack if e.scene_id == scene_id), False)
    def clear(self) -> None: self._stack.clear()
    def __len__(self) -> int: return len(self._stack)
