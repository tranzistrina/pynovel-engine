from pathlib import Path
import json
from vnengine.resources import ResourceRegistry


def test_resource_registry_resolves_and_caches_json(tmp_path: Path):
    (tmp_path / "data").mkdir()
    (tmp_path / "data" / "game.json").write_text(json.dumps({"value": 7}), encoding="utf-8")
    registry = ResourceRegistry(tmp_path)
    registry.register("game", "data/game.json", "json")
    first = registry.load_json("game")
    (tmp_path / "data" / "game.json").write_text(json.dumps({"value": 9}), encoding="utf-8")
    assert registry.load_json("game") is first
    registry.clear_cache()
    assert registry.load_json("game")["value"] == 9


def test_resource_inspection_reports_missing_files(tmp_path: Path):
    registry = ResourceRegistry(tmp_path)
    registry.register("missing", "assets/nope.png", "image")
    result = registry.inspect()
    assert result["count"] == 1
    assert result["resources"][0]["exists"] is False
