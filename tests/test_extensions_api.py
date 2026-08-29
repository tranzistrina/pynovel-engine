from vnengine.extensions.events import EventBus
from vnengine.extensions.scenes import SceneStack
from vnengine.extensions.state import StateRegistry
from vnengine.extensions.system import SystemRegistry


class DummySystem:
    name = "dummy"
    def __init__(self): self.calls = []
    def update(self, dt, state): self.calls.append(("update", dt))
    def handle_event(self, event, state): self.calls.append(("event", event)); return False
    def serialize(self): return {"value": 7}
    def deserialize(self, data): self.calls.append(("load", data))


class DummyScene:
    def __init__(self, name): self.name=name; self.calls=[]
    def enter(self, context): self.calls.append("enter")
    def exit(self): self.calls.append("exit")
    def update(self, dt): self.calls.append("update")
    def handle_input(self, event): self.calls.append(("input", event)); return True
    def draw(self, surface): self.calls.append("draw")


def test_event_bus_priority_and_unsubscribe():
    bus = EventBus(); order=[]
    a = bus.subscribe("x", lambda event: order.append("a") or False, priority=0)
    b = bus.subscribe("x", lambda event: order.append("b") or True, priority=10)
    assert bus.emit("x", {"v": 1}) is True
    assert order == ["b", "a"]
    bus.unsubscribe(a); order.clear(); bus.emit("x")
    assert order == ["b"]
    bus.unsubscribe(b)
    assert bus.emit("x") is False


def test_system_registry_round_trip():
    registry = SystemRegistry(); system = DummySystem(); registry.register(system)
    assert registry.get("dummy") is system
    assert registry.serialize() == {"dummy": {"value": 7}}
    registry.deserialize({"dummy": {"value": 9}})
    assert ("load", {"value": 9}) in system.calls
    registry.unregister("dummy")
    assert registry.get("dummy") is None


def test_namespaced_state_and_dirty_tracking():
    state = StateRegistry(); state.register("campaign", {"day": 1, "factions": {"foo": {"relation": 10}}}, version=2)
    assert state.get("campaign.day") == 1
    state.set("campaign.day", 2)
    state.set("campaign.factions.foo.relation", 12)
    assert state.get("campaign.factions.foo.relation") == 12
    assert state.dirty_namespaces() == ("campaign",)
    payload = state.serialize(); assert payload["campaign"]["version"] == 2
    restored = StateRegistry(); restored.deserialize(payload)
    assert restored.get("campaign.day") == 2
    assert restored.canonical_json() == state.canonical_json()


def test_scene_stack_lifecycle_and_input_focus():
    stack = SceneStack(); base = DummyScene("base"); modal = DummyScene("modal")
    stack.push(base, pause_underlying=False); stack.push(modal, pause_underlying=True)
    assert len(stack) == 2
    assert base.calls == ["enter"]
    assert modal.calls == ["enter"]
    assert stack.handle_input("click") is True
    assert modal.calls[-1] == ("input", "click")
    popped = stack.pop()
    assert popped is modal
    assert modal.calls[-1] == "exit"
    assert stack.current is base
