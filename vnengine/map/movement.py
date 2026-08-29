from __future__ import annotations
from dataclasses import dataclass
from math import hypot
from typing import Any, Callable
from vnengine.map.model import MapDefinition, MapPoint
from vnengine.map.pathfinding import Route


@dataclass(slots=True)
class Movement:
    entity_id: str
    route: Route
    position: MapPoint
    segment: int = 0
    progress: float = 0.0
    speed: float = 100.0
    paused: bool = False

    @property
    def finished(self) -> bool:
        return self.segment >= len(self.route.nodes) - 1


class MovementController:
    """Time-based route movement independent from gameplay/entity storage."""

    def __init__(self, definition: MapDefinition, emit: Callable[[str, dict[str, Any]], None] | None = None):
        self.definition = definition; self.emit = emit or (lambda name, data: None)
        self._nodes = {node.id: node for node in definition.nodes}; self.active: dict[str, Movement] = {}

    def start(self, entity_id: str, route: Route, speed: float = 100.0) -> Movement:
        if speed <= 0: raise ValueError("movement speed must be positive")
        if not route.nodes or route.nodes[0] not in self._nodes: raise ValueError("route starts at an unknown node")
        movement = Movement(entity_id, route, self._nodes[route.nodes[0]].position, speed=speed); self.active[entity_id] = movement
        self.emit("movement.started", {"entity_id": entity_id, "route": list(route.nodes), "speed": speed}); return movement

    def restore(self, payload: dict[str, dict[str, Any]]) -> None:
        self.active.clear()
        for entity_id, data in payload.items():
            route_nodes = tuple(data.get("route", ()))
            if len(route_nodes) < 1 or any(node_id not in self._nodes for node_id in route_nodes):
                raise ValueError(f"invalid movement route for {entity_id}")
            position = data.get("position")
            if not position or len(position) != 2: raise ValueError(f"invalid movement position for {entity_id}")
            route = Route(route_nodes, float(data.get("cost", 0)))
            self.active[entity_id] = Movement(entity_id, route, MapPoint(float(position[0]), float(position[1])), int(data.get("segment", 0)), float(data.get("progress", 0)), float(data.get("speed", 100)), bool(data.get("paused", False)))

    def pause(self, entity_id: str) -> None:
        movement = self._require(entity_id); movement.paused = True; self.emit("movement.paused", {"entity_id": entity_id})
    def resume(self, entity_id: str) -> None:
        movement = self._require(entity_id); movement.paused = False; self.emit("movement.resumed", {"entity_id": entity_id})
    def cancel(self, entity_id: str) -> None:
        movement = self.active.pop(entity_id, None)
        if movement is not None: self.emit("movement.cancelled", {"entity_id": entity_id, "node": movement.route.nodes[movement.segment]})

    def update(self, dt: float) -> None:
        if dt < 0: raise ValueError("dt cannot be negative")
        for movement in tuple(self.active.values()):
            if movement.paused or movement.finished: continue
            remaining = movement.speed * dt
            while remaining > 0 and not movement.finished:
                start = self._nodes[movement.route.nodes[movement.segment]].position; target = self._nodes[movement.route.nodes[movement.segment + 1]].position
                distance = hypot(target.x - start.x, target.y - start.y)
                if distance == 0: movement.segment += 1; movement.progress = 0.0; continue
                segment_remaining = distance * (1.0 - movement.progress); step = min(remaining, segment_remaining)
                movement.progress += step / distance; remaining -= step
                movement.position = MapPoint(start.x + (target.x - start.x) * movement.progress, start.y + (target.y - start.y) * movement.progress)
                self.emit("movement.progress", {"entity_id": movement.entity_id, "position": movement.position, "segment": movement.segment, "progress": movement.progress})
                if movement.progress >= 1.0 - 1e-9:
                    movement.segment += 1; movement.progress = 0.0; movement.position = target
                    if movement.finished: self.active.pop(movement.entity_id, None); self.emit("movement.arrived", {"entity_id": movement.entity_id, "node": movement.route.nodes[-1]})

    def _require(self, entity_id: str) -> Movement:
        try: return self.active[entity_id]
        except KeyError: raise KeyError(f"No active movement: {entity_id}") from None
