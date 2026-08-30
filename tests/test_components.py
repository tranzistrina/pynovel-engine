from vnengine.components import ComponentRegistry, ComponentSystem
from vnengine.map.entities import EntityRegistry, MapEntity
from vnengine.map.model import MapPoint


def test_component_registry_defaults_and_requirements():
    registry = ComponentRegistry()
    registry.register("transform", defaults={"x": 0, "y": 0})
    registry.register("sprite", requires=("transform",), defaults={"visible": True})
    assert registry.create("transform") == {"x": 0, "y": 0}
    assert registry.validate({"sprite": {}}) == ["Component sprite requires transform"]
    assert registry.validate({"transform": {}, "sprite": {}}) == []


def test_entity_registry_uses_component_registry():
    components = ComponentRegistry()
    components.register("transform")
    components.register("sprite", requires=("transform",))
    entities = EntityRegistry(component_registry=components)
    entities.add(MapEntity("hero", MapPoint(0, 0), "town", {"transform": {}}))
    try:
        entities.set_component("hero", "sprite", {})
    except ValueError as exc:
        assert "requires transform" in str(exc)
    else:
        raise AssertionError("Expected component dependency validation to fail")


def test_component_system_processes_matching_entities_only():
    components = ComponentRegistry()
    components.register("health")
    entities = EntityRegistry(component_registry=components)
    entities.add(MapEntity("hero", MapPoint(0, 0), "town", {"health": 10}))
    entities.add(MapEntity("tree", MapPoint(2, 0), "forest"))

    seen = []
    class DamageSystem(ComponentSystem):
        def process(self, entity, dt, state):
            seen.append(entity.id)
            entity.components["health"] -= 1

    system = DamageSystem("damage", requires=("health",))
    assert system.run(0.1, entities, {}) == 1
    assert seen == ["hero"]
    assert entities.get_component("hero", "health") == 9
