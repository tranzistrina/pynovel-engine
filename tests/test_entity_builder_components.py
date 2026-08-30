from vnengine.ai_builder import AIProjectBuilder


def test_builder_entity_components_roundtrip(tmp_path):
    builder = AIProjectBuilder(tmp_path)
    builder.create_project("Demo")
    builder.create_map(width=100, height=100)
    builder.add_node("start", 10, 10)
    builder.add_entity("hero", "start")
    builder.set_entity_component("hero", "actor", {"role": "player"})
    builder.set_entity_component("hero", "health", 100)
    assert builder.document.ensure_map()["entities"][0]["components"]["health"] == 100
    assert builder.remove_entity_component("hero", "health") == 100


def test_builder_batch_component_commands(tmp_path):
    builder = AIProjectBuilder(tmp_path)
    builder.apply([
        {"command": "create_project", "name": "Demo"},
        {"command": "create_map", "width": 100, "height": 100},
        {"command": "add_node", "node_id": "start", "x": 10, "y": 10},
        {"command": "add_entity", "entity_id": "hero", "node_id": "start"},
        {"command": "set_entity_component", "entity_id": "hero", "component": "actor", "value": {"role": "player"}},
    ])
    entity = builder.document.ensure_map()["entities"][0]
    assert entity["components"]["actor"]["role"] == "player"
