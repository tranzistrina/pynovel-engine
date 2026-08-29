from vnengine.map.model import MapDefinition, MapPoint
from vnengine.map.playable import PlayableMap


def make_game_map():
    definition = MapDefinition.from_dict({
        "width": 300, "height": 200,
        "nodes": [{"id": "a", "x": 20, "y": 20}, {"id": "b", "x": 120, "y": 20}],
        "connections": [{"source": "a", "target": "b"}],
    })
    game_map = PlayableMap(definition, hit_radius=15)
    game_map.add_entity("army", "a")
    return game_map


def test_hit_test_prefers_entity_over_node():
    game_map = make_game_map()
    hit = game_map.hit_test(MapPoint(20, 20))
    assert hit.entity_id == "army"
    assert hit.node_id is None


def test_hit_test_returns_node_when_no_entity_is_hit():
    game_map = make_game_map()
    hit = game_map.hit_test(MapPoint(120, 20))
    assert hit.entity_id is None
    assert hit.node_id == "b"


def test_select_at_updates_world_selection():
    game_map = make_game_map()
    hit = game_map.select_at(MapPoint(20, 20))
    assert hit.entity_id == "army"
    assert game_map.world.selection.selected == ("army",)
