import json

from vnengine.dsl import GameDSL
from vnengine.project_runtime import ProjectRuntime


def test_compiled_dsl_registers_and_starts_declarative_scene(tmp_path):
    source = 'project "Demo"\nmap 800 600\nstart main\nscene main\n  say hero "Hello"\nscene forest\n  say hero "Forest"\n'
    GameDSL().compile(source, tmp_path)
    runtime = ProjectRuntime(tmp_path, viewport=(0, 0, 800, 600))
    assert set(("map", "main", "forest")).issubset(set(runtime.scenes.ids()))
    runtime.start()
    assert runtime.scene_id == "main"
    assert runtime.scene.last_text == "Hello"


def test_compiled_dsl_persists_scene_actions(tmp_path):
    source = 'project "Demo"\nscene main\n  say hero "Hello world"\n'
    GameDSL().compile(source, tmp_path)
    payload = json.loads((tmp_path / "scenes.json").read_text(encoding="utf-8"))
    assert payload["main"]["actions"][0] == {"type": "say", "speaker": "hero", "text": "Hello world"}
