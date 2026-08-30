from types import SimpleNamespace

from vnengine.contracts import RuntimeContracts


def test_logical_input_emits_global_and_action_specific_events():
    contracts = RuntimeContracts()
    seen = []
    contracts.subscribe("input.action", lambda event: seen.append((event.name, event.data["action"])))
    contracts.subscribe("input.action.confirm", lambda event: seen.append((event.name, event.data["action"])))

    contracts.bind("confirm", "KEYDOWN", 13)
    assert contracts.dispatch(SimpleNamespace(type=1), event_type="KEYDOWN", code=13)
    assert seen == [("input.action", "confirm"), ("input.action.confirm", "confirm")]


def test_unbound_logical_input_is_not_handled():
    contracts = RuntimeContracts()
    assert not contracts.dispatch(object(), event_type="KEYDOWN", code=13)
