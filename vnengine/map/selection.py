from __future__ import annotations
from dataclasses import dataclass


@dataclass(slots=True)
class Selectable:
    id: str
    enabled: bool = True
    hovered: bool = False
    selected: bool = False
    focused: bool = False


class SelectionModel:
    """Reusable single/multi-selection state for generic map or editor entities."""

    def __init__(self) -> None:
        self._items: dict[str, Selectable] = {}
        self._selected: list[str] = []
        self._focused: str | None = None
        self._hovered: str | None = None

    def register(self, item_id: str, enabled: bool = True) -> Selectable:
        if item_id not in self._items:
            self._items[item_id] = Selectable(item_id, enabled=enabled)
        else:
            self._items[item_id].enabled = enabled
        return self._items[item_id]

    def unregister(self, item_id: str) -> None:
        self._items.pop(item_id, None)
        self._selected = [item for item in self._selected if item != item_id]
        if self._focused == item_id:
            self._focused = None
        if self._hovered == item_id:
            self._hovered = None

    def set_hover(self, item_id: str | None) -> None:
        if self._hovered and self._hovered in self._items:
            self._items[self._hovered].hovered = False
        self._hovered = item_id if item_id in self._items else None
        if self._hovered:
            self._items[self._hovered].hovered = True

    def set_focus(self, item_id: str | None) -> None:
        if self._focused and self._focused in self._items:
            self._items[self._focused].focused = False
        self._focused = item_id if item_id in self._items else None
        if self._focused:
            self._items[self._focused].focused = True

    def select(self, item_id: str, additive: bool = False) -> tuple[str, ...]:
        item = self._items.get(item_id)
        if item is None or not item.enabled:
            return self.selected
        if not additive:
            for selected in self._selected:
                if selected in self._items:
                    self._items[selected].selected = False
            self._selected = []
        if item_id not in self._selected:
            self._selected.append(item_id)
            item.selected = True
        self.set_focus(item_id)
        return self.selected

    def toggle(self, item_id: str) -> tuple[str, ...]:
        item = self._items.get(item_id)
        if item is None or not item.enabled:
            return self.selected
        if item_id in self._selected:
            self._selected.remove(item_id)
            item.selected = False
        else:
            self._selected.append(item_id)
            item.selected = True
            self.set_focus(item_id)
        return self.selected

    def clear(self) -> None:
        for item_id in self._selected:
            if item_id in self._items:
                self._items[item_id].selected = False
        self._selected = []
        self.set_focus(None)

    @property
    def selected(self) -> tuple[str, ...]:
        return tuple(self._selected)

    @property
    def focused(self) -> str | None:
        return self._focused

    @property
    def hovered(self) -> str | None:
        return self._hovered

    def get(self, item_id: str) -> Selectable | None:
        return self._items.get(item_id)
