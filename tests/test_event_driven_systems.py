from vnengine.event_bus import EventBus
from vnengine.systems import SystemRegistry


def test_event_bus_subscription_and_queue_are_deterministic():
    bus = EventBus(); seen = []
    sub = bus.subscribe("ping", lambda data: seen.append(data))
    assert bus.emit("ping", 1) == 1
    bus.queue("ping", 2); bus.queue("ping", 3)
    assert bus.flush() == 2
    assert seen == [1, 2, 3]
    assert bus.unsubscribe(sub) is True
    assert bus.listeners("ping") == 0


def test_system_phases_and_event_subscriptions_roundtrip():
    registry = SystemRegistry()
    registry.register("input", phases=("input",), events=("input.raw",), priority=100)
    registry.register("movement", phases=("update",), after=("input",), priority=50)
    registry.register("render", phases=("render",), after=("movement",))
    assert registry.order() == ("input", "movement", "render")
    assert registry.enabled_specs("update")[0].name == "movement"
    payload = registry.serialize()
    assert payload["input"]["events"] == ["input.raw"]
    assert payload["render"]["phases"] == ["render"]
