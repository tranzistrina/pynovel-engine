from vnengine.ui.hierarchy import can_reparent, clone_node, find_parent, reparent, set_z, translate_nodes


def tree():
    return {
        "type": "panel", "id": "root", "children": [
            {"type": "panel", "id": "left", "children": [
                {"type": "button", "id": "play", "x": 10, "y": 20}
            ]},
            {"type": "panel", "id": "right", "children": []},
        ]
    }


def test_reparent_moves_node_between_panels():
    root = tree()
    assert can_reparent(root, "play", "right")
    assert reparent(root, "play", "right")
    assert find_parent(root, "play")["id"] == "right"
    assert root["children"][0]["children"] == []


def test_reparent_rejects_cycles_and_non_panels():
    root = tree()
    assert not can_reparent(root, "left", "play")
    assert not can_reparent(root, "left", "left")
    assert not reparent(root, "missing", "right")


def test_clone_and_group_helpers():
    root = tree()
    clone = clone_node(root, "play")
    assert clone is not None and clone["id"] == "play_copy"
    nodes = [root["children"][0]["children"][0], clone]
    translate_nodes(nodes, 5, -3)
    assert nodes[0]["x"] == 15 and nodes[0]["y"] == 17
    set_z(nodes, 10)
    assert nodes[0]["z"] == 10 and nodes[1]["z"] == 11
