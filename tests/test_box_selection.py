from vnengine.map.box_selection import BoxSelector
from vnengine.map.model import MapDefinition
from vnengine.map.surface import MapSurface


def test_box_selector_selects_nodes_and_markers():
    definition = MapDefinition.from_dict({
        "width": 1000, "height": 600,
        "nodes": [
            {"id": "a", "x": 100, "y": 100},
            {"id": "b", "x": 250, "y": 180},
            {"id": "c", "x": 700, "y": 500},
        ],
    })
    surface = MapSurface(definition)
    selector = BoxSelector(surface)
    selector.begin((590, 310)); selector.update((760, 500))
    change = selector.finish()
    assert change.selected == ("a", "b")


def test_box_selector_additive_selection():
    definition = MapDefinition.from_dict({
        "width": 1000, "height": 600,
        "nodes": [{"id": "a", "x": 100, "y": 100}, {"id": "b", "x": 700, "y": 500}],
    })
    surface = MapSurface(definition)
    selector = BoxSelector(surface)
    selector.selection.set(["a"])
    selector.begin((1190, 610)); selector.update((1360, 800))
    assert selector.finish(additive=True).selected == ("a", "b")
