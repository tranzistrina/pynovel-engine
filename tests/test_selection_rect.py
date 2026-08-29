from vnengine.editor.selection_rect import Rect, select_intersecting


def test_rect_normalizes_points():
    rect = Rect.from_points(50, 80, 10, 20)
    assert rect == Rect(10, 20, 50, 80)


def test_select_intersecting_keeps_input_order():
    items = [
        ("a", Rect(0, 0, 20, 20)),
        ("b", Rect(40, 40, 60, 60)),
        ("c", Rect(70, 10, 90, 30)),
    ]
    assert select_intersecting(items, Rect.from_points(15, 15, 50, 50)) == ["a", "b"]
