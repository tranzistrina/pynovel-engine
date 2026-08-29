from vnengine.map.model import MapDefinition
from vnengine.map.route_builder import RouteBuilder


def test_route_builder_uses_shortest_path_and_callback():
    definition = MapDefinition.from_dict({
        "width": 1000, "height": 600,
        "nodes": [{"id": "a", "x": 0, "y": 0}, {"id": "b", "x": 1, "y": 0}, {"id": "c", "x": 2, "y": 0}],
        "connections": [
            {"source": "a", "target": "b", "cost": 1},
            {"source": "b", "target": "c", "cost": 1},
            {"source": "a", "target": "c", "cost": 5},
        ],
    })
    routes = []
    route = RouteBuilder(definition, routes.append).build("a", "c")
    assert route.nodes == ("a", "b", "c")
    assert route.cost == 2
    assert routes == [route]


def test_route_builder_handles_unreachable_target():
    definition = MapDefinition.from_dict({"width": 100, "height": 100, "nodes": [{"id": "a", "x": 0, "y": 0}, {"id": "b", "x": 1, "y": 1}]})
    assert RouteBuilder(definition).build("a", "b") is None
