from vnengine.map.multiselect import MultiSelection


def test_multi_selection_preserves_order_and_reports_delta():
    selection = MultiSelection(["a"])
    change = selection.add("b", "a", "c")
    assert change.added == ("b", "c")
    assert change.removed == ()
    assert change.selected == ("a", "b", "c")


def test_multi_selection_toggle_and_remove():
    selection = MultiSelection(["a", "b"])
    assert selection.toggle("b").selected == ("a",)
    assert selection.remove("a").selected == ()
    assert selection.clear().selected == ()
