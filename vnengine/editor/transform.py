from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping, MutableMapping


@dataclass(frozen=True)
class Rect:
    x: float
    y: float
    width: float
    height: float

    @property
    def right(self) -> float:
        return self.x + self.width

    @property
    def bottom(self) -> float:
        return self.y + self.height


def group_bounds(rects: Iterable[Rect]) -> Rect | None:
    items = list(rects)
    if not items:
        return None
    left = min(r.x for r in items)
    top = min(r.y for r in items)
    right = max(r.right for r in items)
    bottom = max(r.bottom for r in items)
    return Rect(left, top, right - left, bottom - top)


def rect_intersects(a: Rect, b: Rect) -> bool:
    return a.x < b.right and a.right > b.x and a.y < b.bottom and a.bottom > b.y


def scale_rect_from_origin(rect: Rect, origin: tuple[float, float], sx: float, sy: float) -> Rect:
    ox, oy = origin
    return Rect(
        ox + (rect.x - ox) * sx,
        oy + (rect.y - oy) * sy,
        max(1.0, rect.width * sx),
        max(1.0, rect.height * sy),
    )


def scale_nodes_from_group(nodes: Iterable[MutableMapping[str, object]], bounds: Rect, sx: float, sy: float) -> None:
    """Scale node x/y/width/height around the group's top-left corner."""
    if bounds.width <= 0 or bounds.height <= 0:
        return
    for node in nodes:
        x = float(node.get("x", 0) or 0)
        y = float(node.get("y", 0) or 0)
        width = float(node.get("width", 1) or 1)
        height = float(node.get("height", 1) or 1)
        scaled = scale_rect_from_origin(Rect(x, y, width, height), (bounds.x, bounds.y), sx, sy)
        node["x"] = int(round(scaled.x))
        node["y"] = int(round(scaled.y))
        node["width"] = max(1, int(round(scaled.width)))
        node["height"] = max(1, int(round(scaled.height)))
        node["anchor"] = "top-left"
