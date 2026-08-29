from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

@dataclass(frozen=True)
class Rect:
    left: float
    top: float
    right: float
    bottom: float

    @classmethod
    def from_points(cls, x1: float, y1: float, x2: float, y2: float) -> "Rect":
        return cls(min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2))

    def intersects(self, other: "Rect") -> bool:
        return not (
            self.right < other.left
            or other.right < self.left
            or self.bottom < other.top
            or other.bottom < self.top
        )

def select_intersecting(items: Iterable[tuple[str, Rect]], selection: Rect) -> list[str]:
    """Return IDs whose bounds intersect the selection rectangle, in input order."""
    return [item_id for item_id, bounds in items if bounds.intersects(selection)]
