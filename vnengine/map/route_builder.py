from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from vnengine.map.model import MapConnection, MapDefinition
from vnengine.map.movement_policy import MovementPolicy
from vnengine.map.pathfinding import Route, shortest_path


@dataclass(frozen=True, slots=True)
class RouteRequest:
    start: str
    goal: str


class RouteBuilder:
    """Build deterministic weighted routes and resolve entity ids when supplied."""

    def __init__(self, definition: MapDefinition, on_route: Callable[[Route], None] | None = None, policy: MovementPolicy | None = None, entity_resolver: Callable[[str], str | None] | None = None):
        self.definition = definition
        self.on_route = on_route
        self.policy = policy
        self.entity_resolver = entity_resolver
        self._nodes = {node.id: node for node in definition.nodes}

    def _resolve_node(self, value: str) -> str:
        if value in self._nodes: return value
        if self.entity_resolver is not None:
            resolved = self.entity_resolver(value)
            if resolved in self._nodes: return resolved
        raise KeyError(f"Unknown route node or entity: {value}")

    def build(self, start: str, goal: str, base_cost: float = 1.0) -> Route | None:
        start_node, goal_node = self._resolve_node(start), self._resolve_node(goal)

        def allowed(source: str, target: str, edge: MapConnection) -> bool:
            return self.policy.can_traverse(source, target) if self.policy else not edge.blocked

        def cost(source: str, target: str, edge: MapConnection) -> float:
            base = edge.cost * base_cost
            return self.policy.cost(source, target, base) if self.policy else base

        route = shortest_path(self.definition, start_node, goal_node, allowed, cost)
        if route is not None and self.on_route is not None: self.on_route(route)
        return route

    def build_many(self, starts: list[str], goal: str, base_cost: float = 1.0) -> dict[str, Route | None]:
        return {start: self.build(start, goal, base_cost) for start in starts}
