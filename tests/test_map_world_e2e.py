from vnengine.map.model import MapDefinition
from vnengine.map.movement_command import MovementCommand
from vnengine.map.route_builder import RouteBuilder
from vnengine.map.world import MapWorld


def test_map_world_end_to_end_move_and_restore_state():
    definition = MapDefinition.from_dict({
        "width": 500, "height": 200,
        "nodes": [{"id": "a", "x": 0, "y": 0}, {"id": "b", "x": 100, "y": 0}, {"id": "c", "x": 200, "y": 0}],
        "connections": [{"source": "a", "target": "b", "cost": 1}, {"source": "b", "target": "c", "cost": 1}],
    })
    world = MapWorld(definition)
    world.add_entity("army_1", "a", components={"type": "army"})
    world.add_entity("army_2", "a", components={"type": "army"})
    world.selection.select("army_1")
    world.selection.select("army_2", additive=True)
    command = MovementCommand(RouteBuilder(definition), world.movement)
    orders = command.execute(world.selection, "c", speed=100)
    assert len(orders) == 2
    world.update(0.5)
    assert world.entities.require("army_1").position.x == 50
    assert world.entities.require("army_2").position.x == 50
    payload = world.serialize()
    restored = MapWorld(definition)
    restored.deserialize(payload)
    assert restored.entities.require("army_1").position.x == 50
    assert restored.selection.selected == ("army_1", "army_2")
    assert "army_1" in restored.movement.active
    restored.update(1.5)
    assert restored.entities.require("army_1").position.x == 200
    assert restored.entities.require("army_1").node_id == "c"
