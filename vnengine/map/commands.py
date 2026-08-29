from __future__ import annotations
from dataclasses import dataclass
from .movement_command import MovementCommand, MovementOrder
from .multiselect import MultiSelection


@dataclass(frozen=True, slots=True)
class CommandResult:
    accepted: tuple[str, ...]
    rejected: tuple[str, ...]


class MapCommandDispatcher:
    """Small command facade for map gameplay systems."""
    def __init__(self, movement: MovementCommand):
        self.movement = movement

    def move_selected(self, selection: MultiSelection, target_node: str, speed: float = 100.0) -> CommandResult:
        orders: list[MovementOrder] = self.movement.execute(selection, target_node, speed)
        accepted = tuple(order.entity_id for order in orders)
        rejected = tuple(entity_id for entity_id in selection.selected if entity_id not in accepted)
        return CommandResult(accepted, rejected)
