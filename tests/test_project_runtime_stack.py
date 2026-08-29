from pathlib import Path
from vnengine.project_runtime import ProjectRuntime
from vnengine.scene_registry import SceneRegistry


class Scene:
    def __init__(self, scene_id, log): self.scene_id = scene_id; self.log = log
    def enter(self): self.log.append((self.scene_id, "enter"))
    def exit(self): self.log.append((self.scene_id, "exit"))
    def pause(self): self.log.append((self.scene_id, "pause"))
    def resume(self): self.log.append((self.scene_id, "resume"))


def test_runtime_push_pop_calls_lifecycle_hooks():
    root = Path(__file__).parents[1] / "examples" / "data"
    log = []; registry = SceneRegistry()
    registry.register("map", lambda c: Scene("map", log))
    registry.register("inventory", lambda c: Scene("inventory", log))
    runtime = ProjectRuntime(root, scenes=registry)
    runtime.start(); runtime.push_scene("inventory")
    assert runtime.stack.ids() == ("map", "inventory")
    runtime.pop_scene()
    assert log == [("map", "enter"), ("map", "pause"), ("inventory", "enter"), ("inventory", "exit"), ("map", "resume")]
