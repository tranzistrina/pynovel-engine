from vnengine.ui.selection import Selection


def project():
    return {
        "type": "panel", "id": "root", "children": [
            {"type": "panel", "id": "group", "x": 0, "y": 0, "children": [
                {"type": "button", "id": "a", "x": 10, "y": 20, "z": 1},
                {"type": "button", "id": "b", "x": 30, "y": 40, "z": 2},
            ]}
        ]
    }


def test_selection_toggle_and_resolve():
    root = project(); selection = Selection()
    selection.toggle("a"); selection.toggle("b"); selection.toggle("a")
    assert selection.ids == ["b"]
    assert [node["id"] for node in selection.resolve(root)] == ["b"]


def test_group_translate_and_z_order():
    root = project(); selection = Selection(["a", "b"])
    selection.apply_delta(root, 5, -10)
    selection.set_z_order(root, 50)
    nodes = {n["id"]: n for n in selection.resolve(root)}
    assert nodes["a"]["x"] == 15 and nodes["a"]["y"] == 10
    assert nodes["b"]["x"] == 35 and nodes["b"]["y"] == 30
    assert nodes["a"]["z"] == 50 and nodes["b"]["z"] == 51
