from vnengine.map.box_controller import BoxSelectionController
from vnengine.map.box_selection import BoxSelector
from vnengine.map.model import MapDefinition
from vnengine.map.surface import MapSurface


def test_box_controller_emits_selection_changed():
    definition = MapDefinition.from_dict({"width": 1000, "height": 600, "nodes": [{"id": "a", "x": 100, "y": 100}]})
    selector = BoxSelector(MapSurface(definition))
    events = []
    controller = BoxSelectionController(selector, lambda name, data: events.append((name, data)))
    controller.begin((590, 310)); controller.update((700, 420)); change = controller.finish()
    assert change.selected == ("a",)
    assert events[0][0] == "map.box_selection_started"
    assert events[-1][0] == "map.selection_changed"
    assert events[-1][1]["selected"] == ["a"]
