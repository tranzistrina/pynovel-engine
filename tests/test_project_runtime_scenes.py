from pathlib import Path
from vnengine.project_runtime import ProjectRuntime
from vnengine.scene_registry import SceneRegistry


def test_project_runtime_switches_registered_scenes():
    root = Path(__file__).parents[1] / "examples" / "data"
    registry = SceneRegistry()
    registry.register("menu", lambda context: {"kind": "menu"})
    runtime = ProjectRuntime(root, scenes=registry)
    runtime.switch_scene("menu")
    assert runtime.scene_id == "menu"
    assert runtime.scene == {"kind": "menu"}


def test_project_runtime_registers_default_map_scene():
    root = Path(__file__).parents[1] / "examples" / "data"
    runtime = ProjectRuntime(root)
    assert runtime.scenes.has("map")
