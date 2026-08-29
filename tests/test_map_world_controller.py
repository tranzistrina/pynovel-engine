from vnengine.map.commands import MapCommandDispatcher
from vnengine.map.model import MapDefinition
from vnengine.map.movement_command import MovementCommand
from vnengine.map.route_builder import RouteBuilder
from vnengine.map.world import MapWorld
from vnengine.map.world_controller import MapWorldController


def test_world_controller_dispatches_move_for_selected_entities():
    definition = MapDefinition.from_dict({
        "width": 200, "height": 100,
        "nodes": [{"id": "a", "x": 0, "y": 0}, {"id": "b", "x": 100, "y": 0}],
        "connections": [{"source": "a", "target": "b", "cost": 1}],
    })
    world = MapWorld(definition)
    world.add_entity("unit", "a")
    world.selection.select("unit")
    events = []
    controller = MapWorldController(world, RouteBuilder(definition), lambda name, data: events.append((name, data)))
    result = controller.move_selected("b", speed=50)
    assert result.accepted == ("unit",)
    controller.update(1.0)
    assert world.entities.require("unit").position.x == 50
    assert events[-1][0] == "map.move_command"
