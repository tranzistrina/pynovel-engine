from vnengine.ai_builder import AIProjectBuilder


def test_apply_is_atomic(tmp_path):
    builder = AIProjectBuilder(tmp_path)
    result = builder.apply([
        {"command": "create_project", "name": "Atomic Demo"},
        {"command": "create_map", "width": 800, "height": 500},
        {"command": "add_node", "node_id": "start", "x": 10, "y": 20},
    ])
    assert result["applied"] == 3
    assert (tmp_path / "project.json").is_file()
    assert (tmp_path / "map.json").is_file()


def test_apply_rolls_back_everything_on_failure(tmp_path):
    builder = AIProjectBuilder(tmp_path)
    try:
        builder.apply([
            {"command": "create_project", "name": "Broken"},
            {"command": "create_map", "width": 100, "height": 100},
            {"command": "add_node", "node_id": "start", "x": 0, "y": 0},
            {"command": "add_connection", "source": "start", "target": "missing"},
        ])
    except ValueError:
        pass
    else:
        raise AssertionError("Expected invalid batch to fail")
    assert not (tmp_path / "project.json").exists()
    assert not (tmp_path / "map.json").exists()
