from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable

Node = dict[str, Any]

@dataclass
class Selection:
    ids: list[str] = field(default_factory=list)

    def clear(self) -> None:
        self.ids.clear()

    def set(self, node_ids: Iterable[str]) -> None:
        seen: set[str] = set()
        self.ids = [node_id for node_id in node_ids if node_id and not (node_id in seen or seen.add(node_id))]

    def toggle(self, node_id: str) -> None:
        if node_id in self.ids:
            self.ids.remove(node_id)
        else:
            self.ids.append(node_id)

    def add(self, node_id: str) -> None:
        if node_id and node_id not in self.ids:
            self.ids.append(node_id)

    def remove(self, node_id: str) -> None:
        if node_id in self.ids:
            self.ids.remove(node_id)

    def contains(self, node_id: str) -> bool:
        return node_id in self.ids

    def resolve(self, root: Node) -> list[Node]:
        wanted = set(self.ids)
        nodes: list[Node] = []
        def walk(node: Node) -> None:
            if node.get("id") in wanted:
                nodes.append(node)
            for child in node.get("children", []):
                walk(child)
        walk(root)
        return nodes

    def apply_delta(self, root: Node, dx: int, dy: int) -> list[Node]:
        from vnengine.ui.hierarchy import translate_nodes
        nodes = self.resolve(root)
        translate_nodes(nodes, dx, dy)
        return nodes

    def set_z_order(self, root: Node, z: int) -> list[Node]:
        from vnengine.ui.hierarchy import set_z
        nodes = self.resolve(root)
        set_z(nodes, z)
        return nodes
