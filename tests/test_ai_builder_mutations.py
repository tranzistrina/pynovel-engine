from vnengine.ai_builder import AIProjectBuilder


def test_batch_supports_edit_and_remove_operations(tmp_path):
    builder = AIProjectBuilder(tmp_path)
    result = builder.apply([
        {"command": "create_project", "name": "Mutation Demo"},
        {"command": "create_map", "width": 500, "height": 300},
        {"command": "add_node", "node_id": "a", "x": 0, "y": 0},
        {"command": "add_node", "node_id": "b", "x": 100, "y": 0},
        {"command": "add_entity", "entity_id": "hero", "node_id": "a"},
        {"command": "set_map_property", "key": "background", "value": "bg.png"},
        {"command": "set_entity_property", "entity_id": "hero", "key": "label", "value": "Hero"},
        {"command": "remove_entity", "entity_id": "hero"},
        {"command": "remove_node", "node_id": "b"},
    ], save=False)
    assert result["applied"] == 9
    assert result["project"]["map"]["nodes"] == 1
    assert result["project"]["map"]["entities"] == 0
