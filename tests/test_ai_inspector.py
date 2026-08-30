from pathlib import Path

from vnengine.ai import AIProjectAPI
from vnengine.project_runtime import ProjectRuntime


ROOT = Path(__file__).parents[1] / "examples" / "data"


def test_ai_describe_contains_project_and_runtime_metadata():
    api = AIProjectAPI(ProjectRuntime(ROOT, viewport=(0, 0, 800, 600)))
    result = api.describe()
    assert result["api_version"] == 2
    assert result["project"]["name"] == "Playable Map Demo"
    assert result["runtime"]["scene_stack"] == []


def test_ai_inspector_reports_map_structure_after_start():
    runtime = ProjectRuntime(ROOT, viewport=(0, 0, 800, 600))
    runtime.start()
    result = AIProjectAPI(runtime).inspect("map")
    assert result["active"] is True
    assert "capital" in result["nodes"]
    assert "army_1" in result["entities"]


def test_ai_validator_accepts_example_project():
    runtime = ProjectRuntime(ROOT, viewport=(0, 0, 800, 600))
    runtime.start()
    result = AIProjectAPI(runtime).validate()
    assert result["valid"] is True
    assert result["errors"] == []
