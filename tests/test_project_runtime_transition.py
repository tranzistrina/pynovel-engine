from pathlib import Path
from vnengine.project_runtime import ProjectRuntime
from vnengine.scene_registry import SceneRegistry


def test_runtime_advances_scene_transition():
    root = Path(__file__).parents[1] / "examples" / "data"
    registry = SceneRegistry(); registry.register("menu", lambda _: object())
    runtime = ProjectRuntime(root, scenes=registry)
    runtime.start(); runtime.push_scene("menu", transition=("fade", 1.0))
    assert runtime.transitions.active
    runtime.update(0.5)
    assert runtime.transitions.active
    runtime.update(0.5)
    assert not runtime.transitions.active
