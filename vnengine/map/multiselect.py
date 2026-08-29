from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True, slots=True)
class SelectionChange:
    added: tuple[str, ...]
    removed: tuple[str, ...]
    selected: tuple[str, ...]


class MultiSelection:
    """Ordered, rendering-independent multi-selection for map entities."""
    def __init__(self, selected: Iterable[str] = ()):
        self._selected: list[str] = list(dict.fromkeys(str(x) for x in selected))

    @property
    def selected(self) -> tuple[str, ...]:
        return tuple(self._selected)

    def set(self, ids: Iterable[str]) -> SelectionChange:
        new = list(dict.fromkeys(str(x) for x in ids)); old = self._selected
        self._selected = new
        return SelectionChange(tuple(x for x in new if x not in old), tuple(x for x in old if x not in new), tuple(new))

    def add(self, *ids: str) -> SelectionChange: return self.set((*self._selected, *ids))
    def remove(self, *ids: str) -> SelectionChange:
        excluded = set(ids); return self.set(x for x in self._selected if x not in excluded)
    def toggle(self, item_id: str) -> SelectionChange:
        return self.remove(item_id) if item_id in self._selected else self.add(item_id)
    def clear(self) -> SelectionChange: return self.set(())
    def contains(self, item_id: str) -> bool: return item_id in self._selected
