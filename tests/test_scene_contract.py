from vnengine.scene import Scene


class DummyScene:
    def enter(self): pass
    def exit(self): pass
    def pause(self): pass
    def resume(self): pass
    def update(self, dt): pass
    def handle_input(self, event): return False
    def render(self, target): pass
    def serialize(self): return {}
    def deserialize(self, payload): pass


def test_scene_contract_is_runtime_checkable_by_shape():
    scene = DummyScene()
    required = ("enter", "exit", "pause", "resume", "update", "handle_input", "render", "serialize", "deserialize")
    assert all(callable(getattr(scene, name, None)) for name in required)
    assert Scene is not None
