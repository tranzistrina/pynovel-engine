from pathlib import Path

from vnengine.project_runtime import ProjectRuntime
from vnengine.declarative_scene import DeclarativeScene


def test_shared_logic_state_survives_scene_switch(tmp_path):
    root = tmp_path
    (root / "project.json").write_text('{"name":"Demo","version":"1.0","map_path":"map.json","start_scene":"a"}\n')
    (root / "map.json").write_text('{"width":100,"height":100,"nodes":[],"connections":[],"entities":[]}\n')
    (root / "scenes.json").write_text('{"a":{"actions":[{"type":"set","variable":"trust","value":3},{"type":"say","speaker":"hero","text":"A"}]},"b":{"actions":[{"type":"if","condition":{"variable":"trust","operator":">=","value":3},"then":[{"type":"set","variable":"door","value":"open"}]},{"type":"say","speaker":"hero","text":"B"}]}}\n')
    class Frontend: _pygame = None
    runtime = ProjectRuntime(root, frontend=Frontend())
    runtime.start()
    assert runtime.logic.get("trust") == 3
    runtime.switch_scene("b")
    assert runtime.logic.get("door") == "open"


def test_logic_is_saved_with_runtime_state(tmp_path):
    root = tmp_path
    (root / "project.json").write_text('{"name":"Demo","version":"1.0","map_path":"map.json","start_scene":"a"}\n')
    (root / "map.json").write_text('{"width":100,"height":100,"nodes":[],"connections":[],"entities":[]}\n')
    runtime = ProjectRuntime(root, viewport=(0,0,1,1))
    runtime.logic.set("score", 42)
    state = runtime.save_state()
    assert state["logic"]["variables"]["score"] == 42
