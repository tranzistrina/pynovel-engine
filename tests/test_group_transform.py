from vnengine.editor.group_transform import (
    bounding_box, translate, scale, align_left, align_top,
    distribute_horizontal, distribute_vertical,
)


def nodes():
    return [
        {"id": "a", "x": 10, "y": 20, "width": 100, "height": 50},
        {"id": "b", "x": 150, "y": 80, "width": 50, "height": 40},
        {"id": "c", "x": 300, "y": 40, "width": 80, "height": 60},
    ]


def test_bounding_box():
    assert bounding_box(nodes()) == (10, 20, 380, 140)


def test_translate_and_scale():
    items = nodes()
    translate(items, 5, -10)
    assert (items[0]["x"], items[0]["y"]) == (15, 10)
    scale(items, 2, 2, origin=(15, 10))
    assert items[0]["width"] == 200
    assert items[0]["height"] == 100


def test_alignment_and_distribution():
    items = nodes()
    align_left(items)
    assert {n["x"] for n in items} == {10}
    align_top(items)
    assert {n["y"] for n in items} == {20}

    items = nodes()
    distribute_horizontal(items)
    assert items[1]["x"] == 155

    items = nodes()
    distribute_vertical(items)
    assert items[1]["y"] == 50
