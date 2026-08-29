from __future__ import annotations
from vnengine.map.box_selection import BoxSelector
from vnengine.map.controller import MapEvent


class BoxSelectionController:
    """Connects rectangle selection to the engine event bus."""

    def __init__(self, selector: BoxSelector, emit=None):
        self.selector = selector
        self.emit = emit or (lambda *args: None)

    def begin(self, pos: tuple[int, int]) -> None:
        self.selector.begin(pos)
        self._emit("map.box_selection_started", {"position": pos})

    def update(self, pos: tuple[int, int]) -> None:
        self.selector.update(pos)

    def finish(self, additive: bool = False):
        change = self.selector.finish(additive)
        self._emit("map.selection_changed", {
            "added": list(change.added),
            "removed": list(change.removed),
            "selected": list(change.selected),
            "additive": additive,
        })
        return change

    def cancel(self) -> None:
        self.selector.cancel()
        self._emit("map.box_selection_cancelled", {})

    def _emit(self, name: str, data: dict) -> None:
        try:
            self.emit(name, data)
        except TypeError:
            self.emit(MapEvent(name, None, data))
