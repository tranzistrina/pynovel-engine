import pygame
from vnengine.map.model import MapDefinition
from vnengine.map.surface import MapMarker, MapSurface


def test_map_surface_selection_and_route():
    pygame.init()
    try:
        definition = MapDefinition.from_dict({
            "width": 1000, "height": 600,
            "nodes": [{"id": "a", "x": 100, "y": 100}, {"id": "b", "x": 300, "y": 100}],
            "connections": [{"source": "a", "target": "b"}],
        })
        view = MapSurface(definition)
        view.camera.x = 100; view.camera.y = 100
        assert view.select_at((640, 360)).id == "a"
        view.set_route(["a", "b"])
        assert view.route == ["a", "b"]
        view.add_marker(MapMarker("army", definition.nodes[0].position))
        assert view.select_at((640, 360)).id == "army"
    finally:
        pygame.quit()


def test_map_surface_zoom_keeps_anchor_stable():
    pygame.init()
    try:
        definition = MapDefinition.from_dict({"width": 2000, "height": 1200})
        view = MapSurface(definition)
        before = view.screen_to_map((700, 400))
        view.zoom_at(2.0, (700, 400))
        after = view.screen_to_map((700, 400))
        assert abs(before.x - after.x) < 1e-6
        assert abs(before.y - after.y) < 1e-6
    finally:
        pygame.quit()
