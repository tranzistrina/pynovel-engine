from vnengine.project_runner import ProjectRunner


class Runtime:
    def __init__(self): self.calls = []
    def start(self): self.calls.append("start")
    def stop(self): self.calls.append("stop")
    def handle_input(self, event): self.calls.append(("input", event))
    def update(self, dt): self.calls.append(("update", dt))
    def render(self, target): self.calls.append(("render", target))


def test_runner_stops_on_quit_event_without_forwarding_it():
    runtime = Runtime()
    class Event: type = "QUIT"
    runner = ProjectRunner(runtime, poll_events=lambda: [Event()], target="screen")
    runner.running = True
    runner.step(1 / 60)
    assert runner.running is False
    assert not any(call[0] == "input" for call in runtime.calls if isinstance(call, tuple))
