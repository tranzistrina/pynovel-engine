from pathlib import Path
import pytest
from vnengine.ai import AIProjectAPI
from vnengine.project_runtime import ProjectRuntime


ROOT = Path(__file__).parents[1] / "examples" / "data"


def test_ai_api_returns_json_safe_project_description():
    api = AIProjectAPI(ProjectRuntime(ROOT, viewport=(0, 0, 800, 600)))
    result = api.describe()
    assert result["api_version"] == 1
    assert "scenes" in result["capabilities"]
    assert result["scene_stack"] == []


def test_ai_api_restricts_runtime_commands():
    api = AIProjectAPI(ProjectRuntime(ROOT, viewport=(0, 0, 800, 600)))
    with pytest.raises(ValueError):
        api.call("eval", expression="1+1")
