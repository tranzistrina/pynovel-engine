from pathlib import Path
import pytest

from vnengine.ai import AIProjectAPI
from vnengine.project_runtime import ProjectRuntime


ROOT = Path(__file__).parents[1] / "examples" / "data"


def test_ai_command_schema_is_machine_readable():
    api = AIProjectAPI(ProjectRuntime(ROOT, viewport=(0, 0, 800, 600)))
    schema = api.command_schema()
    assert schema["api_version"] == 1
    assert "switch_scene" in schema["commands"]
    assert schema["commands"]["switch_scene"]["required"] == ["scene_id"]


def test_ai_call_rejects_missing_and_extra_arguments():
    api = AIProjectAPI(ProjectRuntime(ROOT, viewport=(0, 0, 800, 600)))
    with pytest.raises(ValueError, match="Missing required arguments"):
        api.call("switch_scene")
    with pytest.raises(ValueError, match="Unexpected arguments"):
        api.call("stop", extra=True)
