from vnengine.ai_builder import AIProjectBuilder


def test_ai_builder_creates_project_and_map(tmp_path):
    builder = AIProjectBuilder(tmp_path)
    manifest = builder.create_project("AI Demo")
    assert manifest["start_scene"] == "map"
    builder.create_map(width=1000, height=600)
    builder.add_node("start", 100, 100, label="Start")
    builder.add_node("town", 400, 200, label="Town")
    builder.add_connection("start", "town", cost=2)
    builder.add_entity("hero", "start", components={"kind": "character"})
    inspected = builder.inspect()
    assert inspected["map"] == {"exists": True, "nodes": 2, "connections": 1, "entities": 1}


def test_ai_builder_rejects_invalid_references(tmp_path):
    builder = AIProjectBuilder(tmp_path)
    builder.create_map(width=100, height=100)
    builder.add_node("start", 0, 0)
    try:
        builder.add_connection("start", "missing")
    except ValueError as exc:
        assert "Unknown node" in str(exc)
    else:
        raise AssertionError("Expected invalid connection to fail")
