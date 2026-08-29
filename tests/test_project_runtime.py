from pathlib import Path
from vnengine.project_runtime import ProjectRuntime


def test_project_runtime_lifecycle():
    root = Path(__file__).parents[1] / "examples" / "data"
    events = []
    runtime = ProjectRuntime(root, emit=lambda name, data: events.append((name, data)))
    runtime.start()
    assert runtime.running
    assert runtime.scene_id == "map"
    assert runtime.world.entities.require("army_1").node_id == "capital"
    state = runtime.save_state()
    runtime.stop()
    assert not runtime.running
    runtime.load_state(state)
    assert runtime.running
    assert events[0][0] == "runtime.started"
    assert events[-1][0] == "runtime.loaded"
