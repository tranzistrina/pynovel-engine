from dataclasses import dataclass, field

from vnengine.extensions.scenes import SceneStack


@dataclass
class SceneDouble:
    name: str
    events: list[str] = field(default_factory=list)
    fail_enter: bool = False

    def enter(self, context):
        self.events.append("enter")
        if self.fail_enter:
            raise RuntimeError("enter failed")

    def exit(self): self.events.append("exit")
    def update(self, dt): self.events.append("update")
    def handle_input(self, event): return False
    def draw(self, surface): pass
    def pause(self): self.events.append("pause")
    def resume(self): self.events.append("resume")


def test_push_pop_pauses_and_resumes_previous_scene():
    stack = SceneStack()
    root = SceneDouble("root")
    overlay = SceneDouble("overlay")
    stack.push(root)
    stack.push(overlay)
    assert root.events == ["enter", "pause"]
    stack.pop()
    assert root.events == ["enter", "pause", "resume"]


def test_failed_push_restores_previous_scene_state():
    stack = SceneStack()
    root = SceneDouble("root")
    broken = SceneDouble("broken", fail_enter=True)
    stack.push(root)
    try:
        stack.push(broken)
    except RuntimeError:
        pass
    else:
        raise AssertionError("expected RuntimeError")
    assert stack.current is root
    assert root.events == ["enter", "pause", "resume"]
    assert broken.events == ["enter"]
