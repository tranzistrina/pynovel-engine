from __future__ import annotations

import json

from vnengine.animation.timeline_runtime import TimelinePlayer
from vnengine.script.parser import VNParser


def test_parser_accepts_play_animation_and_alias():
    story = VNParser().parse('play_animation AliceEnter\nanimation BobIdle\n')
    assert [a.kind for a in story.actions] == ["play_animation", "play_animation"]
    assert story.actions[0].data["name"] == "AliceEnter"
    assert story.actions[1].data["name"] == "BobIdle"


def test_timeline_player_accepts_single_timeline(tmp_path):
    payload = {
        "name": "AliceEnter",
        "loop": False,
        "tracks": [
            {"target": "Alice", "property": "x", "keys": [
                {"time": 0.0, "value": 0.0, "easing": "linear"},
                {"time": 1.0, "value": 100.0, "easing": "linear"},
            ]}
        ],
    }
    (tmp_path / "animation.json").write_text(json.dumps(payload), encoding="utf-8")
    player = TimelinePlayer(tmp_path)
    assert "AliceEnter" in player.timelines
    assert player.play("AliceEnter") is True
    update = player.update(0.5)["AliceEnter"]
    assert update[("Alice", "x")] == 50.0
