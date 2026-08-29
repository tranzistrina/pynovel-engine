from types import SimpleNamespace
from vnengine.extensions.input import InputMap
from vnengine.extensions.runtime import ExtensibleRuntime
from vnengine.core.model import Story


def test_runtime_dispatches_logical_input_actions_and_handlers():
    runtime = ExtensibleRuntime(Story(actions=[], labels={}, title="test"), ".")
    runtime.input_map.bind("confirm", "KEYDOWN", 13)
    seen = []
    runtime.register_input_handler("confirm", lambda event, rt: seen.append((event.key, rt)) or True)
    event = SimpleNamespace(type=999, key=13, mod=0)
    # 999 is intentionally accepted as an opaque event type when no pygame mapping exists.
    assert runtime.dispatch_input(event) is True
    assert seen == [(13, runtime)]


def test_input_map_is_persisted_in_save_bundle(tmp_path):
    runtime = ExtensibleRuntime(Story(actions=[], labels={}, title="test"), ".")
    runtime.input_map.bind("pause", "KEYDOWN", 27)
    path = tmp_path / "save.json"
    runtime.save_bundle(path, project_version="7")

    restored = ExtensibleRuntime(Story(actions=[], labels={}, title="test"), ".")
    restored.load_bundle(path, project_version="7")
    assert restored.input_map.actions_for("KEYDOWN", 27) == ("pause",)
