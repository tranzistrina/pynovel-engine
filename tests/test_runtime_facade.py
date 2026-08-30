from __future__ import annotations

from vnengine.runtime_compat import RuntimeFacade


class FakeRuntime:
    def __init__(self):
        self.running = False
        self.calls = []

    def start(self, **kwargs):
        self.calls.append(("start", kwargs)); self.running = True

    def handle_input(self, event):
        self.calls.append(("input", event)); return event == "handled"

    def update(self, dt): self.calls.append(("update", dt))
    def render(self, target): self.calls.append(("render", target))
    def save_state(self): return {"value": 7, "running": self.running}
    def load_state(self, state): self.calls.append(("restore", state))
    def stop(self): self.calls.append(("stop",)); self.running = False


def test_facade_runs_one_deterministic_step():
    runtime = FakeRuntime(); facade = RuntimeFacade(runtime)
    facade.start(mode="test")
    result = facade.step(0.25, events=["handled", "ignored"], target="screen")
    assert result["handled_events"] == 1
    assert result["running"] is True
    assert result["state"]["value"] == 7
    assert ("update", 0.25) in runtime.calls
    assert ("render", "screen") in runtime.calls


def test_facade_restore_and_capabilities():
    runtime = FakeRuntime(); facade = RuntimeFacade(runtime)
    facade.restore({"value": 9})
    assert ("restore", {"value": 9}) in runtime.calls
    assert all(facade.capabilities().values())
    facade.stop(); assert runtime.running is False
