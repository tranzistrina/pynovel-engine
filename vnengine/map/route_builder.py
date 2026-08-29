from __future__ import annotations
from dataclasses import dataclass
from typing import Callable
from vnengine.map.pathfinding import Route, shortest_path
from vnengine.map.model import MapConnection, MapDefinition
from vnengine.map.movement_policy import MovementPolicy


@dataclass(frozen=True, slots=True)
class RouteRequest:
    start: str
    goal: str


class RouteBuilder:
    """Builds graph routes with optional movement policy hooks."""
    def __init__(self, definition: MapDefinition, on_route: Callable[[Route], None] | None = None, policy: MovementPolicy | None = None):
        self.definition = definition; self.on_route = on_route; self.policy = policy

    def build(self, start: str, goal: str, base_cost: float = 1.0) -> Route | None:
        def allowed(source: str, target: str, edge: MapConnection) -> bool:
            return self.policy.can_traverse(source, target) if self.policy else True
        def cost(source: str, target: str, edge: MapConnection) -> float:
            base = edge.cost * base_cost
            return self.policy.cost(source, target, base) if self.policy else base
        route = shortest_path(self.definition, start, goal, allowed, cost)
        if route is not None and self.on_route is not None: self.on_route(route)
        return route

    def build_many(self, starts: list[str], goal: str, base_cost: float = 1.0) -> dict[str, Route | None]:
        return {start: self.build(start, goal, base_cost) for start in starts}
