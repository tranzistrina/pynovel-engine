from pathlib import Path
from types import SimpleNamespace

from vnengine.core.model import Action, Story
from vnengine.extensions.runtime import ExtensibleRuntime


class System:
    name = "demo"
    def __init__(self): self.value = 7
    def update(self, dt, state): pass
    def handle_event(self, event, state): return False
    def serialize(self): return {"value": self.value}
    def deserialize(self, data): self.value = int(data["value"])


def test_extensible_runtime_bundle_restores_state_and_audio(tmp_path: Path):
    story = Story(actions=[Action("end", {})], labels={}, title="test", variables={"score": 1})
    runtime = ExtensibleRuntime(story, tmp_path)
    system = System(); runtime.register_system(system)
    runtime.state.variables["score"] = 42
    runtime.audio.channel("music").current = "theme.ogg"
    runtime.audio.channel("music").loop = True
    runtime.audio.channel("music").paused = True

    path = tmp_path / "save.json"
    runtime.save_bundle(path, project_version="1")

    restored = ExtensibleRuntime(story, tmp_path)
    restored_system = System(); restored_system.value = 0; restored.register_system(restored_system)
    restored.load_bundle(path, project_version="1")

    assert restored.state.variables["score"] == 42
    assert restored.systems.get("demo").value == 7
    music = restored.audio.channel("music")
    assert music.current == "theme.ogg"
    assert music.loop is True
    assert music.paused is True
