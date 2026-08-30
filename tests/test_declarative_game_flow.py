import json

from vnengine.dsl import GameDSL
from vnengine.project_runtime import ProjectRuntime


def write_game(root):
    source = '''
project "Flow Demo"
version "1.0"
var trust 2
start intro
scene intro
  say hero "Hello"
  choice "Go" if trust >= 2 -> good
  choice "Leave" -> bad
scene good
  set finished true
  say hero "Good"
scene bad
  set finished false
  say hero "Bad"
'''
    GameDSL().compile(source, root)


def test_dsl_logic_and_runtime_shared_state(tmp_path):
    write_game(tmp_path)
    assert json.loads((tmp_path / "project.json").read_text())["variables"]["trust"] == 2
    runtime = ProjectRuntime(tmp_path, viewport=(0, 0, 800, 600))
    runtime.start()
    scene = runtime.scene
    assert runtime.logic.get("trust") == 2
    assert scene.last_text == "Hello"
    assert scene._choose(0)
    assert runtime.scene_id == "good"
    assert runtime.logic.get("finished") is True


def test_runtime_save_restore_includes_logic(tmp_path):
    write_game(tmp_path)
    runtime = ProjectRuntime(tmp_path, viewport=(0, 0, 800, 600))
    runtime.start(); runtime.logic.set("score", 9)
    state = runtime.save_state()
    restored = ProjectRuntime(tmp_path, viewport=(0, 0, 800, 600))
    restored.load_state(state)
    assert restored.logic.get("score") == 9
    assert restored.scene_id == "intro"
