from dataclasses import dataclass

import pytest

from vnengine.runtime_protocol import CoreRuntimeAdapter, RuntimeProtocol, require_runtime


@dataclass
class DummyState:
    running: bool = True
    index: int = 0
    variables: dict = None
    history: list = None
    background_path: str | None = None


class DummyCore:
    def __init__(self):
        self.state = DummyState(variables={}, history=[])
        self.started = 0
        self.updated = []
        self.drawn = []

    def new_game(self): self.started += 1; self.state.running = True
    def update(self, dt): self.updated.append(dt)
    def draw(self, target): self.drawn.append(target)


def test_core_adapter_satisfies_runtime_contract():
    runtime = CoreRuntimeAdapter(DummyCore())
    assert isinstance(runtime, RuntimeProtocol)
    require_runtime(runtime)
    runtime.start(); runtime.update(0.25); runtime.render("screen")
    assert runtime.running
    assert runtime.runtime.started == 1
    assert runtime.runtime.updated == [0.25]
    assert runtime.runtime.drawn == ["screen"]


def test_require_runtime_rejects_incomplete_objects():
    with pytest.raises(TypeError, match="missing"):
        require_runtime(object())


def test_core_adapter_round_trips_state():
    core = DummyCore()
    adapter = CoreRuntimeAdapter(core)
    core.state.index = 7
    core.state.variables = {"score": 10}
    state = adapter.save_state()
    core.state.index = 0
    core.state.variables = {}
    adapter.load_state(state)
    assert core.state.index == 7
    assert core.state.variables == {"score": 10}
