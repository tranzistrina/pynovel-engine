from vnengine.map import Camera2D, MapConnection, MapDefinition, MapNode, MapPoint, SelectionModel, shortest_path


def test_camera_round_trip_and_zoom_anchor():
    camera = Camera2D(x=500, y=300, zoom=2, viewport_width=1000, viewport_height=600)
    point = MapPoint(560, 330)
    screen = camera.map_to_screen(point)
    restored = camera.screen_to_map(screen)
    assert restored == point
    anchor = MapPoint(700, 350)
    before = camera.screen_to_map(anchor)
    camera.set_zoom(3, anchor)
    assert camera.screen_to_map(anchor) == before


def test_deterministic_weighted_pathfinding():
    definition = MapDefinition(
        1000, 1000,
        nodes=(
            MapNode("a", MapPoint(0, 0)),
            MapNode("b", MapPoint(1, 0)),
            MapNode("c", MapPoint(2, 0)),
            MapNode("d", MapPoint(1, 1)),
        ),
        connections=(
            MapConnection("a", "b", 2),
            MapConnection("b", "c", 2),
            MapConnection("a", "d", 1),
            MapConnection("d", "c", 1),
        ),
    )
    route = shortest_path(definition, "a", "c")
    assert route is not None
    assert route.nodes == ("a", "d", "c")
    assert route.cost == 2


def test_selection_hover_focus_and_multiselect():
    selection = SelectionModel()
    selection.register("army_a")
    selection.register("army_b")
    selection.register("disabled", enabled=False)
    assert selection.select("army_a") == ("army_a",)
    assert selection.select("army_b", additive=True) == ("army_a", "army_b")
    selection.set_hover("army_b")
    assert selection.hovered == "army_b"
    assert selection.get("army_b").hovered is True
    selection.set_focus("army_a")
    assert selection.focused == "army_a"
    assert selection.toggle("army_a") == ("army_b",)
    assert selection.select("disabled") == ("army_b",)
