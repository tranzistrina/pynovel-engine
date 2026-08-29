from pathlib import Path

from vnengine.project_runtime import ProjectRuntime


ROOT = Path(__file__).parents[1] / "examples" / "data"


def test_data_project_manifest_bootstraps_map_runtime():
    runtime = ProjectRuntime(ROOT, viewport=(0, 0, 800, 600))
    assert runtime.project.manifest.start_scene == "map"
    assert runtime.scenes.has("map")


def test_runtime_can_save_initial_scene_state():
    runtime = ProjectRuntime(ROOT, viewport=(0, 0, 800, 600))
    runtime.start()
    state = runtime.save_state()
    assert state["scene"] == "map"
    assert state["scene_stack"] == ["map"]
