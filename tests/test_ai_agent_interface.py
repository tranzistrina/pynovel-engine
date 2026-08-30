from pathlib import Path

from vnengine.agent import AIAgentInterface


ROOT = Path(__file__).parents[1] / "examples" / "data"


def test_agent_plan_rejects_unknown_and_extra_arguments():
    agent = AIAgentInterface(ROOT)
    result = agent.plan([
        {"command": "add_node", "node_id": "x", "x": 1, "y": 2, "bogus": True},
        {"command": "not_a_command"},
    ])
    assert not result["valid"]
    assert any(item["code"] == "unexpected_argument" for item in result["diagnostics"])
    assert any(item["code"] == "unknown_command" for item in result["diagnostics"])


def test_agent_dry_run_never_writes_changes(tmp_path):
    agent = AIAgentInterface(tmp_path)
    result = agent.dry_run([
        {"command": "create_project", "name": "Demo"},
        {"command": "create_map", "width": 800, "height": 600},
        {"command": "add_node", "node_id": "start", "x": 10, "y": 20},
    ])
    assert result["committed"] is False
    assert result["applied"] == 3
    assert not (tmp_path / "project.json").exists()
    assert result["preview"]["map"]["nodes"] == 1


def test_agent_apply_returns_validation(tmp_path):
    agent = AIAgentInterface(tmp_path)
    result = agent.apply([
        {"command": "create_project", "name": "Demo"},
        {"command": "create_map", "width": 800, "height": 600},
        {"command": "add_node", "node_id": "start", "x": 10, "y": 20},
        {"command": "add_entity", "entity_id": "hero", "node_id": "start"},
    ])
    assert result["committed"] is True
    assert result["validation"]["valid"] is True
    assert (tmp_path / "project.json").exists()
    assert (tmp_path / "map.json").exists()
