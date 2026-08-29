from pathlib import Path
from vnengine.map import load_map_definition, load_playable_map


def test_load_example_map_definition():
    path = Path(__file__).parents[1] / "examples" / "data" / "map.json"
    definition = load_map_definition(path)
    assert definition.width == 1200
    assert len(definition.nodes) == 4


def test_load_example_playable_map():
    path = Path(__file__).parents[1] / "examples" / "data" / "map.json"
    game_map = load_playable_map(path)
    assert game_map.world.entities.require("army_1").node_id == "capital"
    assert game_map.world.entities.require("army_1").components["kind"] == "army"
