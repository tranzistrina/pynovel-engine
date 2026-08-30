from vnengine.runtime_compat import RuntimeFacade


class FakeRuntime:
    def __init__(self):
        self.running = False
        self.time = 0.0
        self.inputs = []

    def start(self, **kwargs):
        self.running = True

    def update(self, dt):
        self.time += dt

    def handle_input(self, event):
        self.inputs.append(event)
        return True

    def render(self, target):
        return None

    def save_state(self):
        return {"time": round(self.time, 6), "inputs": list(self.inputs)}

    def load_state(self, state):
        self.time = float(state["time"])
        self.inputs = list(state["inputs"])

    def stop(self):
        self.running = False


def test_facade_fixed_timestep_steps_only_complete_updates():
    facade = RuntimeFacade(FakeRuntime(), fixed_timestep=0.1, max_steps=4)
    facade.start()
    result = facade.step(0.25)
    assert result["state"]["time"] == 0.2
    assert facade.capabilities()["fixed_timestep"] is True


def test_facade_profiler_is_exposed():
    facade = RuntimeFacade(FakeRuntime(), profiling=True)
    facade.start()
    result = facade.step(0.1, events=["confirm"])
    assert result["handled_events"] == 1
    assert set(result["profile"]) == {"input", "update", "render"}
    assert result["profile"]["input"]["calls"] == 1
    assert facade.capabilities()["profiling"] is True
