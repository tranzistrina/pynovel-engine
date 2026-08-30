from pathlib import Path
import pytest

from vnengine.ai import AIProjectAPI
from vnengine.ai_schema import command_schema
from vnengine.project_runtime import ProjectRuntime


ROOT = Path(__file__).parents[1] / "examples" / "data"


def test_api_uses_shared_command_schema():
    api = AIProjectAPI(ProjectRuntime(ROOT, viewport=(0, 0, 800, 600)))
    assert api.command_schema() == command_schema()


def test_api_rejects_unexpected_arguments():
    api = AIProjectAPI(ProjectRuntime(ROOT, viewport=(0, 0, 800, 600)))
    with pytest.raises(ValueError, match="Unexpected arguments"):
        api.call("start", scene_id="map")
