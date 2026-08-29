from vnengine.map.controller import MapController
from vnengine.map.interaction import MapAction, MapInteraction
from vnengine.map.model import MapDefinition
from vnengine.map.surface import MapSurface


def make_interaction():
    definition = MapDefinition.from_dict({
        "width": 1000, "height": 600,
        "nodes": [{"id": "a", "x": 100, "y": 100}, {"id": "b", "x": 300, "y": 100}],
    })
    surface = MapSurface(definition)
    surface.camera.x = 100; surface.camera.y = 100
    events = []
    return MapInteraction(MapController(surface, lambda event: events.append(event)), events.append), events


def test_double_click_emits_semantic_action():
    interaction, events = make_interaction()
    interaction.pointer_down((640, 360), 1, 1000)
    interaction.pointer_down((640, 360), 1, 1200)
    assert any(isinstance(e, MapAction) and e.name == "map.double_click" for e in events)


def test_context_click_emits_targeted_action():
    interaction, events = make_interaction()
    interaction.pointer_down((640, 360), 3, 1000)
    action = next(e for e in events if isinstance(e, MapAction))
    assert action.name == "map.context_action"
    assert action.target_id == "a"


def test_route_gesture_is_externalizable():
    interaction, events = make_interaction()
    interaction.begin_route("a")
    interaction.extend_route("b")
    interaction.finish_route(["a", "b"])
    assert [e.name for e in events if isinstance(e, MapAction)] == ["map.route_started", "map.route_extended", "map.route_created"]
