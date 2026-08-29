from __future__ import annotations
from dataclasses import dataclass
from typing import Callable
from vnengine.map.pathfinding import Route, shortest_path
from vnengine.map.model import MapDefinition


@dataclass(frozen=True, slots=True)
class RouteRequest:
    start: str
    goal: str


class RouteBuilder:
    """Builds graph routes without attaching movement/gameplay rules."""

    def __init__(self, definition: MapDefinition, on_route: Callable[[Route], None] | None = None):
        self.definition = definition
        self.on_route = on_route

    def build(self, start: str, goal: str) -> Route | None:
        route = shortest_path(self.definition, start, goal)
        if route is not None and self.on_route is not None:
            self.on_route(route)
        return route

    def build_many(self, starts: list[str], goal: str) -> dict[str, Route | None]:
        return {start: self.build(start, goal) for start in starts}
