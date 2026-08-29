from vnengine.map.model import MapDefinition
from vnengine.map.world import MapWorld


def make_world():
    return MapWorld(MapDefinition.from_dict({
        "width": 100, "height": 100,
        "nodes": [{"id": "a", "x": 0, "y": 0}, {"id": "b", "x": 10, "y": 0}],
        "connections": [{"source": "a", "target": "b", "cost": 1}],
    }))


def test_world_entity_lifecycle_and_selection():
    world = make_world()
    entity = world.add_entity("e1", "a", components={"kind": "unit"})
    assert entity.position.x == 0
    world.selection.select("e1")
    assert world.selection.selected == ("e1",)
    removed = world.remove_entity("e1")
    assert removed is entity
    assert world.entities.get("e1") is None
    assert world.selection.selected == ()


def test_world_serializes_and_restores_entities_and_selection():
    world = make_world()
    world.add_entity("e1", "a")
    world.add_entity("e2", "b")
    world.selection.select("e2")
    payload = world.serialize()

    restored = make_world()
    restored.deserialize(payload)
    assert {e.id for e in restored.entities.all()} == {"e1", "e2"}
    assert restored.selection.selected == ("e2",)
