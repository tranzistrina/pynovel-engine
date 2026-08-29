from vnengine.editor.transform import Rect, group_bounds, rect_intersects, scale_rect_from_origin, scale_nodes_from_group


def test_group_bounds_and_intersection():
    bounds = group_bounds([Rect(10, 20, 100, 40), Rect(80, 10, 60, 80)])
    assert bounds == Rect(10, 10, 130, 80)
    assert rect_intersects(bounds, Rect(100, 70, 20, 20))
    assert not rect_intersects(bounds, Rect(200, 200, 10, 10))


def test_scale_rect_from_origin():
    result = scale_rect_from_origin(Rect(20, 30, 40, 10), (10, 10), 2, 3)
    assert result == Rect(30, 70, 80, 30)


def test_scale_nodes_from_group():
    nodes = [
        {"id": "a", "x": 10, "y": 20, "width": 20, "height": 10},
        {"id": "b", "x": 40, "y": 30, "width": 10, "height": 20},
    ]
    scale_nodes_from_group(nodes, Rect(10, 20, 40, 30), 2, 2)
    assert nodes[0]["x"] == 10 and nodes[0]["y"] == 20
    assert nodes[0]["width"] == 40 and nodes[0]["height"] == 20
    assert nodes[1]["x"] == 70 and nodes[1]["y"] == 40
    assert nodes[1]["width"] == 20 and nodes[1]["height"] == 40
