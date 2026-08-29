from __future__ import annotations
from vnengine.map.model import MapPoint
from vnengine.map.surface import MapSurface
from vnengine.map.multiselect import MultiSelection, SelectionChange


class BoxSelector:
    """Screen-space rectangle selection for map nodes and markers."""

    def __init__(self, surface: MapSurface, selection: MultiSelection | None = None):
        self.surface = surface
        self.selection = selection or MultiSelection()
        self._start: tuple[int, int] | None = None
        self._current: tuple[int, int] | None = None

    @property
    def active(self) -> bool:
        return self._start is not None

    def begin(self, pos: tuple[int, int]) -> None:
        self._start = pos
        self._current = pos

    def update(self, pos: tuple[int, int]) -> None:
        if self.active:
            self._current = pos

    def cancel(self) -> None:
        self._start = None
        self._current = None

    def finish(self, additive: bool = False) -> SelectionChange:
        if not self.active or self._current is None:
            return SelectionChange((), (), self.selection.selected)
        x1, y1 = self._start; x2, y2 = self._current
        left, right = sorted((x1, x2)); top, bottom = sorted((y1, y2))
        ids: list[str] = []
        for node in self.surface.definition.nodes:
            x, y = self.surface.map_to_screen(node.position)
            if left <= x <= right and top <= y <= bottom:
                ids.append(node.id)
        for marker in self.surface.markers.values():
            if marker.visible:
                x, y = self.surface.map_to_screen(marker.position)
                if left <= x <= right and top <= y <= bottom:
                    ids.append(marker.id)
        self.cancel()
        return self.selection.add(*ids) if additive else self.selection.set(ids)

    def rect(self) -> tuple[int, int, int, int] | None:
        if not self.active or self._current is None:
            return None
        x1, y1 = self._start; x2, y2 = self._current
        left, right = sorted((x1, x2)); top, bottom = sorted((y1, y2))
        return left, top, right - left, bottom - top
