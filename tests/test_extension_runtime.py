from vnengine.core.model import Story
from vnengine.extensions import Event, GameSystem
from vnengine.extensions.runtime import ExtensibleRuntime
from vnengine.script.parser import VNParser


class CounterSystem:
    name = "counter"

    def __init__(self):
        self.calls = 0
        self.last = None

    def update(self, dt, state):
        self.calls += 1

    def handle_event(self, event, state):
        return False

    def serialize(self):
        return {"calls": self.calls}

    def deserialize(self, data):
        self.calls = int(data.get("calls", 0))

    def ping(self, *args):
        self.last = list(args)


def test_parser_accepts_project_commands():
    story = VNParser().parse(
        'call_system counter ping one two\n'
        'emit strategy.day_started 7\n'
        'set_state strategy.day 7\n'
        'open_scene strategy\n'
        'close_scene strategy\n'
    )
    assert [a.kind for a in story.actions] == [
        "call_system", "emit", "set_state", "open_scene", "close_scene"
    ]
    assert story.actions[0].data["args"] == ["one", "two"]


def test_extension_runtime_dispatches_system_and_state():
    story = VNParser().parse(
        'call_system counter ping one two\n'
        'set_state strategy.day 7\n'
        'emit strategy.day_started 7\n'
        'end\n'
    )
    runtime = ExtensibleRuntime(story, ".")
    counter = CounterSystem()
    runtime.register_system(counter)
    seen = []
    runtime.subscribe("strategy.day_started", lambda event: seen.append(event.data))

    runtime.advance()

    assert counter.last == ["one", "two"]
    assert runtime.get_state("strategy.day") == 7
    assert seen == [{"args": ["7"]}]


def test_extension_runtime_updates_registered_systems():
    runtime = ExtensibleRuntime(Story([], {}), ".")
    counter = CounterSystem()
    runtime.register_system(counter)
    runtime.update(0.25)
    assert counter.calls == 1
