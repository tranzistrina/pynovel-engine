from vnengine.systems import SystemRegistry


def test_system_order_respects_dependencies_and_priority():
    systems = SystemRegistry()
    systems.register("render", after=("movement",))
    systems.register("movement", priority=1)
    systems.register("input", before=("movement",), priority=5)
    assert systems.order() == ("input", "movement", "render")


def test_system_data_roundtrip_and_cycle_detection():
    systems = SystemRegistry()
    systems.register_data({
        "a": {"kind": "logic", "priority": 2, "settings": {"rate": 1}},
        "b": {"kind": "render", "after": ["a"]},
    })
    assert systems.serialize()["a"]["settings"]["rate"] == 1
    assert systems.order() == ("a", "b")

    cyclic = SystemRegistry()
    cyclic.register("a", after=("b",))
    cyclic.register("b", after=("a",))
    try:
        cyclic.order()
    except ValueError as exc:
        assert "cycle" in str(exc).lower()
    else:
        raise AssertionError("Expected system dependency cycle")


def test_system_definition_validation_rejects_self_reference():
    systems = SystemRegistry()
    systems.register("logic", before=("logic",))
    assert "cannot order itself" in systems.validate_definitions()[0]
