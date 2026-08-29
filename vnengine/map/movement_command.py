from __future__ import annotations
from dataclasses import dataclass
from vnengine.map.movement import MovementController, Movement
from vnengine.map.multiselect import MultiSelection
from vnengine.map.route_builder import RouteBuilder


@dataclass(frozen=True, slots=True)
class MovementOrder:
    entity_id: str
    route: object


class MovementCommand:
    """Creates movement orders for a selection without owning game entities."""
    def __init__(self, routes: RouteBuilder, movement: MovementController, emit=None):
        self.routes = routes; self.movement = movement; self.emit = emit or (lambda name, data: None)

    def execute(self, selection: MultiSelection, target_node: str, speed: float = 100.0) -> list[MovementOrder]:
        orders: list[MovementOrder] = []
        for entity_id in selection.selected:
            route = self.routes.build(entity_id, target_node)
            if route is None:
                self.emit("movement.order_unreachable", {"entity_id": entity_id, "target": target_node}); continue
            self.movement.start(entity_id, route, speed); orders.append(MovementOrder(entity_id, route))
        self.emit("movement.order_created", {"target": target_node, "entities": [o.entity_id for o in orders]})
        return orders

    def execute_with_policy(self, selection: MultiSelection, target_node: str, speed: float = 100.0) -> list[MovementOrder]:
        """Alias emphasizing that RouteBuilder may apply its configured policy."""
        return self.execute(selection, target_node, speed)
