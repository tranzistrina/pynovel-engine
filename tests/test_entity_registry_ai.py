from vnengine.map.entities import EntityRegistry, MapEntity
from vnengine.map.model import MapPoint


def test_entity_handles_components_and_queries():
    registry = EntityRegistry()
    hero = registry.add(MapEntity("hero", MapPoint(1, 2), "town"))
    registry.add(MapEntity("guard", MapPoint(3, 4), "town", {"actor": {"role": "enemy"}}))
    assert hero.id == "hero"
    registry.set_component(hero, "actor", {"role": "player"})
    assert registry.get_component("hero", "actor")["role"] == "player"
    assert [entity.id for entity in registry.query(component="actor")] == ["hero", "guard"]
    assert [entity.id for entity in registry.query(node_id="town")] == ["hero", "guard"]


def test_entity_batch_and_deterministic_serialization():
    registry = EntityRegistry()
    registry.add(MapEntity("b", MapPoint(2, 3), "town", {"hp": 4}))
    registry.add(MapEntity("a", MapPoint(1, 2), "town", {"hp": 5}))
    registry.batch_set_component([("a", "buff", "speed"), ("b", "buff", "armor")])
    serialized = registry.serialize()
    assert list(serialized) == ["a", "b"]
    assert serialized["a"]["components"]["buff"] == "speed"


def test_entity_deserialize_rejects_bad_payload():
    registry = EntityRegistry()
    try:
        registry.deserialize({"hero": {"position": [1]}})
    except ValueError as exc:
        assert "Invalid entity position" in str(exc)
    else:
        raise AssertionError("Expected invalid position to fail")
