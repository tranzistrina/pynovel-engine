from vnengine.map.model import MapDefinition
from vnengine.map.movement import MovementController
from vnengine.map.pathfinding import Route


def make_controller(events):
    definition = MapDefinition.from_dict({
        "width": 500, "height": 200,
        "nodes": [{"id": "a", "x": 0, "y": 0}, {"id": "b", "x": 100, "y": 0}],
    })
    return MovementController(definition, lambda name, data: events.append((name, data)))


def test_movement_reaches_target_and_emits_events():
    events = []; controller = make_controller(events)
    controller.start("army", Route(("a", "b"), 100), speed=100)
    controller.update(0.5)
    assert controller.active["army"].position.x == 50
    controller.update(0.5)
    assert "army" not in controller.active
    assert events[0][0] == "movement.started"
    assert events[-1][0] == "movement.arrived"


def test_movement_pause_resume_and_cancel():
    events = []; controller = make_controller(events)
    controller.start("army", Route(("a", "b"), 100), speed=100)
    controller.pause("army"); controller.update(1.0)
    assert controller.active["army"].position.x == 0
    controller.resume("army"); controller.update(0.25)
    assert controller.active["army"].position.x == 25
    controller.cancel("army")
    assert "army" not in controller.active
