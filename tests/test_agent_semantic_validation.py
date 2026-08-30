import json

from vnengine.agent import AIAgentInterface


def test_validator_catches_unresolved_scene_references(tmp_path):
    (tmp_path / "project.json").write_text(json.dumps({"name":"Demo","version":"1.0","map_path":"map.json","start_scene":"main"}))
    (tmp_path / "map.json").write_text(json.dumps({"width":100,"height":100,"nodes":[],"connections":[],"entities":[]}))
    (tmp_path / "scenes.json").write_text(json.dumps({"main":{"actions":[{"type":"goto","target":"missing"}]}}))
    result = AIAgentInterface(tmp_path).validate()
    assert result["valid"] is False
    assert any(item["code"] == "unresolved_goto" for item in result["errors"])


def test_validator_accepts_valid_scene_reference(tmp_path):
    (tmp_path / "project.json").write_text(json.dumps({"name":"Demo","version":"1.0","map_path":"map.json","start_scene":"main"}))
    (tmp_path / "map.json").write_text(json.dumps({"width":100,"height":100,"nodes":[],"connections":[],"entities":[]}))
    (tmp_path / "scenes.json").write_text(json.dumps({"main":{"actions":[{"type":"goto","target":"end"},{"type":"label","label":"end"}]}}))
    result = AIAgentInterface(tmp_path).validate()
    assert result["valid"] is True
