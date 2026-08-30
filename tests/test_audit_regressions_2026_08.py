from __future__ import annotations

import json

from vnengine.agent import AIAgentInterface
from vnengine.declarative_scene import DeclarativeScene
from vnengine.dsl import GameDSL
from vnengine.map.playable import PlayableMap
from vnengine.map.model import MapDefinition


def test_agent_validate_and_diagnose_are_live(tmp_path):
    (tmp_path / "project.json").write_text(json.dumps({
        "name": "test",
        "version": "1",
        "map_path": "map.json",
        "start_scene": "map",
    }), encoding="utf-8")
    (tmp_path / "map.json").write_text(json.dumps({
        "width": 100,
        "height": 100,
        "nodes": [],
        "connections": [],
        "entities": [],
    }), encoding="utf-8")
    agent = AIAgentInterface(tmp_path)
    validation = agent.validate()
    diagnosis = agent.diagnose()
    assert validation["valid"] is True
    assert diagnosis["valid"] is True
    assert diagnosis["next"]


def test_agent_accepts_legacy_scenario_manifest(tmp_path):
    (tmp_path / "project.json").write_text(json.dumps({
        "name": "legacy",
        "version": 1,
        "scenario": "game.vn",
    }), encoding="utf-8")
    (tmp_path / "game.vn").write_text('say Alice "Hello"\n', encoding="utf-8")
    assert AIAgentInterface(tmp_path).validate()["valid"] is True


def test_dsl_supports_background_color_and_equals_literals():
    parsed = GameDSL().parse('''
project "Demo"
var gold = 10
scene main
background_color "24,24,32"
say hero "Hello"
''')
    assert parsed.project["variables"]["gold"] == 10
    assert parsed.scenes["main"]["background_color"] == (24, 24, 32)


def test_declarative_scene_choice_without_condition_is_available():
    class Logic:
        def __init__(self):
            self.events = []
        def execute(self, action):
            pass
    class Scenes:
        def ids(self): return ("main",)
    class Runtime:
        logic = Logic()
        assets = None
        frontend = None
        scenes = Scenes()
        def evaluate(self, expression): return True
    scene = DeclarativeScene({"actions": [{"type": "choice", "text": "Continue", "target": "main"}]}, Runtime())
    assert len(scene._choices()) == 1


def test_playable_map_exposes_definition_through_world():
    definition = MapDefinition.from_dict({
        "width": 100,
        "height": 100,
        "nodes": [{"id": "n", "x": 0, "y": 0}],
        "connections": [],
        "entities": [],
    })
    playable = PlayableMap(definition)
    assert playable.world.definition is definition
