from pathlib import Path

from vnengine import __version__
from vnengine.core.model import Action, Story
from vnengine.core.save_bundle import SaveBundle
from vnengine.extensions.input import InputMap
from vnengine.extensions.system import SystemRegistry
from vnengine.map.model import MapDefinition
from vnengine.map.playable import PlayableMap


def test_story_can_be_created_without_explicit_labels():
    story = Story([Action("end")])
    assert story.labels == {}


def test_system_registry_exposes_items_for_legacy_callers():
    assert SystemRegistry().items() == ()


def test_input_map_normalizes_numeric_event_codes():
    mapping = InputMap()
    mapping.bind("confirm", "13", 13)
    assert mapping.actions_for(13, "13") == ("confirm",)


def test_save_bundle_roundtrip_is_deterministic(tmp_path: Path):
    path = tmp_path / "save.json"
    bundle = SaveBundle("0.40.0", "1")
    bundle.state = {"value": 7}
    bundle.save(path)
    first = path.read_text(encoding="utf-8")
    loaded = SaveBundle.load(path)
    loaded.save(path)
    second = path.read_text(encoding="utf-8")
    assert first == second


def test_entity_route_resolves_entity_to_its_current_node():
    definition = MapDefinition.from_dict({
        "width": 500, "height": 500,
        "nodes": [
            {"id": "a", "x": 0, "y": 0},
            {"id": "b", "x": 100, "y": 0},
        ],
        "connections": [{"source": "a", "target": "b", "cost": 1}],
    })
    game_map = PlayableMap(definition)
    game_map.add_entity("army_1", "a")
    route = game_map.routes.build("army_1", "b")
    assert route is not None
    assert route.nodes == ("a", "b")
