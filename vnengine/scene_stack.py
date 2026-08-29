from __future__ import annotations
from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class SceneEntry:
    scene_id: str
    scene: Any


class SceneStack:
    """Stack of active runtime scenes for overlays, menus and temporary modes."""
    def __init__(self) -> None:
        self._stack: list[SceneEntry] = []

    def push(self, scene_id: str, scene: Any) -> Any:
        self._stack.append(SceneEntry(scene_id, scene))
        return scene

    def pop(self) -> Any:
        if not self._stack:
            raise IndexError("Cannot pop an empty scene stack")
        return self._stack.pop().scene

    @property
    def current(self) -> Any | None:
        return self._stack[-1].scene if self._stack else None

    @property
    def current_id(self) -> str | None:
        return self._stack[-1].scene_id if self._stack else None

    def ids(self) -> tuple[str, ...]:
        return tuple(entry.scene_id for entry in self._stack)

    def clear(self) -> None:
        self._stack.clear()

    def __len__(self) -> int:
        return len(self._stack)
