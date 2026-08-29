from __future__ import annotations

from copy import deepcopy
from typing import Any, Iterator

Node = dict[str, Any]


def iter_nodes(root: Node) -> Iterator[Node]:
    yield root
    for child in root.get("children", []):
        yield from iter_nodes(child)


def find_by_id(root: Node, node_id: str) -> Node | None:
    for node in iter_nodes(root):
        if node.get("id") == node_id:
            return node
    return None


def find_parent(root: Node, target_id: str) -> Node | None:
    for node in iter_nodes(root):
        for child in node.get("children", []):
            if child.get("id") == target_id:
                return node
    return None


def contains_id(root: Node, target_id: str, search_id: str) -> bool:
    start = find_by_id(root, target_id)
    if start is None:
        return False
    return find_by_id(start, search_id) is not None


def can_reparent(root: Node, node_id: str, new_parent_id: str) -> bool:
    if node_id == new_parent_id:
        return False
    node = find_by_id(root, node_id)
    parent = find_by_id(root, new_parent_id)
    if node is None or parent is None:
        return False
    if contains_id(root, node_id, new_parent_id):
        return False
    return parent.get("type", "panel") == "panel"


def reparent(root: Node, node_id: str, new_parent_id: str) -> bool:
    if not can_reparent(root, node_id, new_parent_id):
        return False
    source_parent = find_parent(root, node_id)
    target_parent = find_by_id(root, new_parent_id)
    if source_parent is None or target_parent is None:
        return False
    for index, child in enumerate(source_parent.get("children", [])):
        if child.get("id") == node_id:
            moved = source_parent["children"].pop(index)
            target_parent.setdefault("children", []).append(moved)
            return True
    return False


def clone_node(root: Node, node_id: str, new_id: str | None = None) -> Node | None:
    node = find_by_id(root, node_id)
    if node is None:
        return None
    clone = deepcopy(node)
    base = new_id or f"{node_id}_copy"
    ids = {item.get("id") for item in iter_nodes(root)}
    candidate = base
    suffix = 1
    while candidate in ids:
        suffix += 1
        candidate = f"{base}{suffix}"
    clone["id"] = candidate
    return clone


def append_clone(root: Node, node_id: str, parent_id: str | None = None) -> Node | None:
    clone = clone_node(root, node_id)
    if clone is None:
        return None
    parent = find_by_id(root, parent_id) if parent_id else find_parent(root, node_id)
    if parent is None:
        parent = root
    parent.setdefault("children", []).append(clone)
    return clone


def translate_nodes(nodes: list[Node], dx: int, dy: int) -> None:
    for node in nodes:
        try:
            node["x"] = int(node.get("x", 0)) + dx
        except (TypeError, ValueError):
            node["x"] = dx
        try:
            node["y"] = int(node.get("y", 0)) + dy
        except (TypeError, ValueError):
            node["y"] = dy
        node["anchor"] = "top-left"


def set_z(nodes: list[Node], z: int) -> None:
    for index, node in enumerate(nodes):
        node["z"] = z + index
