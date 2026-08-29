from vnengine.map.model import MapDefinition
from vnengine.map.movement import MovementController
from vnengine.map.movement_command import MovementCommand
from vnengine.map.multiselect import MultiSelection
from vnengine.map.route_builder import RouteBuilder


def test_movement_command_starts_selected_entities():
    definition = MapDefinition.from_dict({
        "width": 500, "height": 200,
        "nodes": [
            {"id": "a", "x": 0, "y": 0}, {"id": "b", "x": 10, "y": 0}, {"id": "c", "x": 20, "y": 0},
        ],
        "connections": [{"source": "a", "target": "b", "cost": 1}, {"source": "b", "target": "c", "cost": 1}],
    })
    events = []
    movement = MovementController(definition, lambda name, data: events.append((name, data)))
    command = MovementCommand(RouteBuilder(definition), movement)
    orders = command.execute(MultiSelection(["a", "b"]), "c", speed=10)
    assert [o.entity_id for o in orders] == ["a", "b"]
    assert set(movement.active) == {"a", "b"}
    assert events[-1][0] == "movement.order_created"


def test_movement_command_reports_unreachable_entities():
    definition = MapDefinition.from_dict({"width": 100, "height": 100, "nodes": [{"id": "a", "x": 0, "y": 0}, {"id": "c", "x": 20, "y": 0}]})
    events = []
    movement = MovementController(definition, lambda name, data: events.append((name, data)))
    command = MovementCommand(RouteBuilder(definition), movement)
    assert command.execute(MultiSelection(["a"]), "c") == []
    assert events[0][0] == "movement.order_unreachable"
