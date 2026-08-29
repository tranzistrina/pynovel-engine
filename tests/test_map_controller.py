from vnengine.map.controller import MapController
from vnengine.map.model import MapDefinition
from vnengine.map.surface import MapMarker, MapSurface


def test_controller_emits_selection_and_route_events():
    definition = MapDefinition.from_dict({
        "width": 1000, "height": 600,
        "nodes": [{"id": "a", "x": 100, "y": 100}, {"id": "b", "x": 300, "y": 100}],
    })
    surface = MapSurface(definition)
    surface.camera.x = 100; surface.camera.y = 100
    events = []
    controller = MapController(surface, events.append)
    controller.select((640, 360))
    controller.set_route(["a", "b"])
    assert [event.name for event in events] == ["map.node_selected", "map.route_changed"]
    assert events[0].target_id == "a"
    assert events[1].data["nodes"] == ["a", "b"]


def test_controller_prioritizes_marker_selection():
    definition = MapDefinition.from_dict({"width": 1000, "height": 600, "nodes": [{"id": "a", "x": 100, "y": 100}]})
    surface = MapSurface(definition); surface.camera.x = 100; surface.camera.y = 100
    surface.add_marker(MapMarker("army", definition.nodes[0].position))
    events = []; controller = MapController(surface, events.append)
    controller.select((640, 360))
    assert events[0].name == "map.marker_selected"
    assert events[0].target_id == "army"
