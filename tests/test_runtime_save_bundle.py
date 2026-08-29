from vnengine.core.model import Story
from vnengine.extensions.runtime import ExtensibleRuntime


class System:
    name = "campaign"

    def __init__(self):
        self.value = 0

    def update(self, dt, state):
        pass

    def handle_event(self, event, state):
        return False

    def serialize(self):
        return {"value": self.value}

    def deserialize(self, data):
        self.value = int(data["value"])


def test_runtime_save_bundle_restores_extension_state_and_rng(tmp_path):
    runtime = ExtensibleRuntime(Story([], {}), ".")
    system = System(); system.value = 17
    runtime.register_system(system)
    runtime.register_state_namespace("campaign", {"day": 4})
    runtime.set_state("campaign.day", 9)
    runtime.rng.seed(123)
    runtime.rng.randint(1, 100)
    expected = runtime.rng.randint(1, 100)
    path = tmp_path / "bundle.json"
    runtime.save_bundle(path, "game-1")

    restored = ExtensibleRuntime(Story([], {}), ".")
    restored_system = System(); restored.register_system(restored_system)
    restored.register_state_namespace("campaign", {"day": 0})
    restored.load_bundle(path, "game-1")

    assert restored.get_state("campaign.day") == 9
    assert restored_system.value == 17
    assert restored.rng.randint(1, 100) == expected
