from pathlib import Path
from vnengine.project_runtime import ProjectRuntime
from vnengine.scene_registry import SceneRegistry


class Scene:
    def __init__(self): self.inputs = []; self.frames = 0
    def handle_input(self, event): self.inputs.append(event); return True
    def render(self, target): self.frames += 1


def test_runtime_forwards_input_and_render():
    root = Path(__file__).parents[1] / "examples" / "data"
    scene = Scene(); registry = SceneRegistry(); registry.register("test", lambda _: scene)
    runtime = ProjectRuntime(root, scenes=registry); runtime.switch_scene("test"); runtime.running = True
    token = object()
    assert runtime.handle_input(token) is True
    runtime.render(object())
    assert scene.inputs == [token]
    assert scene.frames == 1
