from pathlib import Path
from vnengine.map.scene import MapScene
from vnengine.map.loader import load_playable_map


def test_map_scene_wraps_playable_map():
    root = Path(__file__).parents[1] / "examples" / "data"
    game_map = load_playable_map(root / "map.json")
    scene = MapScene(game_map, (0, 0, 800, 600))
    assert scene.world is game_map
    assert scene.surface.definition is game_map.definition
    scene.update(0.0)
    assert scene.serialize()["entities"]["army_1"]["node_id"] == "capital"
