from __future__ import annotations
import heapq
from dataclasses import dataclass

from .model import MapConnection, MapDefinition


@dataclass(frozen=True, slots=True)
class Route:
    nodes: tuple[str, ...]
    cost: float


def shortest_path(definition: MapDefinition, start: str, goal: str) -> Route | None:
    if start == goal:
        return Route((start,), 0.0)
    edges: dict[str, list[MapConnection]] = {node.id: [] for node in definition.nodes}
    for edge in definition.connections:
        if not edge.blocked and edge.source in edges and edge.target in edges:
            edges[edge.source].append(edge)
    for items in edges.values():
        items.sort(key=lambda edge: (edge.target, edge.cost))

    queue: list[tuple[float, str]] = [(0.0, start)]
    distances = {start: 0.0}
    previous: dict[str, str] = {}
    visited: set[str] = set()
    while queue:
        distance, current = heapq.heappop(queue)
        if current in visited:
            continue
        visited.add(current)
        if current == goal:
            path = [goal]
            while path[-1] != start:
                path.append(previous[path[-1]])
            path.reverse()
            return Route(tuple(path), distance)
        for edge in edges.get(current, []):
            candidate = distance + max(0.0, edge.cost)
            if candidate < distances.get(edge.target, float("inf")):
                distances[edge.target] = candidate
                previous[edge.target] = current
                heapq.heappush(queue, (candidate, edge.target))
    return None
