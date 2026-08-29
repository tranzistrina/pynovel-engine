from pathlib import Path
from vnengine.project_runtime import ProjectRuntime
from vnengine.project_runner import ProjectRunner
from vnengine.scene_registry import SceneRegistry


class Scene:
    def __init__(self, log): self.log = log
    def enter(self): self.log.append("enter")
    def exit(self): self.log.append("exit")
    def handle_input(self, event): self.log.append(("input", event)); return True
    def update(self, dt): self.log.append(("update", dt))
    def render(self, target): self.log.append(("render", target))


def test_runner_drives_runtime_loop():
    root = Path(__file__).parents[1] / "examples" / "data"; log = []
    scene = Scene(log); registry = SceneRegistry(); registry.register("test", lambda _: scene)
    runtime = ProjectRuntime(root, scenes=registry); runtime.switch_scene("test"); runtime.running = True
    events = iter([("click",), (type("Quit", (), {"quit": True})(),)])
    runner = ProjectRunner(runtime, poll_events=lambda: next(events, ()), target="screen", present=lambda t: log.append(("present", t)))
    runner.running = True; runner.step(1/60); runner.running = False
    assert ("click",) in [x[1] for x in log if isinstance(x, tuple) and x and x[0] == "input"]
    assert ("render", "screen") in log
    assert ("present", "screen") in log
