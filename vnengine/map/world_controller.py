from __future__ import annotations
from typing import Any
from .commands import MapCommandDispatcher
from .movement_command import MovementCommand
from .route_builder import RouteBuilder
from .world import MapWorld


class MapWorldController:
    """High-level map facade for UI/input code."""
    def __init__(self, world: MapWorld, routes: RouteBuilder, emit=None):
        self.world = world
        self.command = MapCommandDispatcher(MovementCommand(routes, world.movement, emit))
        self.emit = emit or (lambda name, data: None)

    def move_selected(self, target_node: str, speed: float = 100.0):
        result = self.command.move_selected(self.world.selection, target_node, speed)
        self.emit("map.move_command", {"target": target_node, "accepted": list(result.accepted), "rejected": list(result.rejected)})
        return result

    def update(self, dt: float) -> None:
        self.world.update(dt)
