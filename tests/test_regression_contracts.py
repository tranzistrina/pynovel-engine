from __future__ import annotations

from pathlib import Path

from vnengine.animation.timeline import Timeline
from vnengine.core.save_bundle import SaveBundle
from vnengine.map.model import MapDefinition
from vnengine.map.route_builder import RouteBuilder


def test_timeline_samples_exact_endpoint_and_stops_playback() -> None:
    timeline = Timeline("move")
    timeline.add_keyframe("hero", "x", 0.0, 0.0)
    timeline.add_keyframe("hero", "x", 1.0, 100.0)
    timeline.play()
    assert timeline.sample(0.5)[("hero", "x")] == 50.0
    timeline.update(1.0)
    assert timeline.sample()[("hero", "x")] == 100.0
    assert timeline.playing is False


def test_save_bundle_roundtrip_is_deterministic(tmp_path: Path) -> None:
    bundle = SaveBundle("0.40.0", "1")
    bundle.state = {"score": 5, "flags": {"intro": True}}
    first = tmp_path / "one.json"
    second = tmp_path / "two.json"
    bundle.save(first)
    loaded = SaveBundle.load(first)
    loaded.save(second)
    assert loaded.state == bundle.state
    assert first.read_text(encoding="utf-8") == second.read_text(encoding="utf-8")


def test_route_builder_rejects_unknown_nodes_cleanly() -> None:
    definition = MapDefinition.from_dict({"width": 100, "height": 100, "nodes": [{"id": "a", "x": 0, "y": 0}]})
    builder = RouteBuilder(definition)
    try:
        builder.build("missing", "a")
    except KeyError as exc:
        assert "Unknown route node" in str(exc)
    else:
        raise AssertionError("Expected unknown route node error")
