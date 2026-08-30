from dataclasses import dataclass

import pytest

from vnengine.runtime_adapter import RuntimeAdapter
from vnengine.runtime_protocol import CoreRuntimeAdapter, require_runtime
from vnengine.extensions.runtime import ExtensibleRuntime
from vnengine.core.model import Action, Story


@dataclass
class DummyRuntime:
    running: bool = False
    value: int = 0

    def start(self, **kwargs): self.running = True
    def update(self, dt): self.value += 1
    def handle_input(self, event): return event == "handled"
    def render(self, target): return None
    def save_state(self): return {"value": self.value}
    def load_state(self, state): self.value = int(state["value"])
    def stop(self): self.running = False


def test_runtime_adapter_normalizes_lifecycle():
    runtime = DummyRuntime()
    adapter = RuntimeAdapter(runtime)
    adapter.start(); adapter.step(); assert adapter.running and adapter.snapshot() == {"value": 1}
    adapter.restore({"value": 9}); assert adapter.snapshot() == {"value": 9}
    adapter.stop(); assert not adapter.running


def test_require_runtime_rejects_incomplete_object():
    with pytest.raises(TypeError):
        require_runtime(object())


def test_extensible_runtime_exposes_protocol_surface():
    story = Story(title="test", actions=(Action("end", {}),), variables={})
    runtime = ExtensibleRuntime(story, ".")
    assert require_runtime(runtime) is runtime
    state = runtime.save_state()
    assert "runtime" in state and "audio" in state and "input_map" in state
