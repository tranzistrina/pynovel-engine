from __future__ import annotations

from typing import Any, Iterable

Node = dict[str, Any]


def _num(node: Node, key: str, default: int = 0) -> int:
    try:
        return int(node.get(key, default))
    except (TypeError, ValueError):
        return default


def bounding_box(nodes: Iterable[Node]) -> tuple[int, int, int, int] | None:
    items = list(nodes)
    if not items:
        return None
    left = min(_num(n, "x") for n in items)
    top = min(_num(n, "y") for n in items)
    right = max(_num(n, "x") + max(1, _num(n, "width", 1)) for n in items)
    bottom = max(_num(n, "y") + max(1, _num(n, "height", 1)) for n in items)
    return left, top, right, bottom


def translate(nodes: Iterable[Node], dx: int, dy: int) -> None:
    for node in nodes:
        node["x"] = _num(node, "x") + dx
        node["y"] = _num(node, "y") + dy
        node["anchor"] = "top-left"


def scale(nodes: Iterable[Node], sx: float, sy: float, origin: tuple[int, int] | None = None) -> None:
    items = list(nodes)
    box = bounding_box(items)
    if box is None:
        return
    ox, oy = origin or (box[0], box[1])
    for node in items:
        x = _num(node, "x")
        y = _num(node, "y")
        w = max(1, _num(node, "width", 1))
        h = max(1, _num(node, "height", 1))
        node["x"] = round(ox + (x - ox) * sx)
        node["y"] = round(oy + (y - oy) * sy)
        node["width"] = max(1, round(w * sx))
        node["height"] = max(1, round(h * sy))
        node["anchor"] = "top-left"


def align_left(nodes: Iterable[Node]) -> None:
    items = list(nodes)
    if not items:
        return
    x = min(_num(n, "x") for n in items)
    translate(items, 0, 0)
    for node in items:
        node["x"] = x


def align_top(nodes: Iterable[Node]) -> None:
    items = list(nodes)
    if not items:
        return
    y = min(_num(n, "y") for n in items)
    for node in items:
        node["y"] = y
        node["anchor"] = "top-left"


def distribute_horizontal(nodes: Iterable[Node]) -> None:
    items = sorted(list(nodes), key=lambda n: _num(n, "x"))
    if len(items) < 3:
        return
    first = items[0]
    last = items[-1]
    start = _num(first, "x")
    end = _num(last, "x")
    step = (end - start) / (len(items) - 1)
    for index, node in enumerate(items[1:-1], start=1):
        node["x"] = round(start + step * index)
        node["anchor"] = "top-left"


def distribute_vertical(nodes: Iterable[Node]) -> None:
    items = sorted(list(nodes), key=lambda n: _num(n, "y"))
    if len(items) < 3:
        return
    first = items[0]
    last = items[-1]
    start = _num(first, "y")
    end = _num(last, "y")
    step = (end - start) / (len(items) - 1)
    for index, node in enumerate(items[1:-1], start=1):
        node["y"] = round(start + step * index)
        node["anchor"] = "top-left"
