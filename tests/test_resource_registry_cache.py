from pathlib import Path

from vnengine.resources import ResourceRegistry


def test_json_cache_is_bounded_and_deterministic(tmp_path: Path):
    (tmp_path / "one.json").write_text('{"value": 1}', encoding="utf-8")
    (tmp_path / "two.json").write_text('{"value": 2}', encoding="utf-8")
    registry = ResourceRegistry(tmp_path, max_cache=1)
    registry.register("one", "one.json", "json")
    registry.register("two", "two.json", "json")

    assert registry.load_json("one")["value"] == 1
    assert registry.load_json("one")["value"] == 1
    assert registry.load_json("two")["value"] == 2
    assert registry.load_json("one")["value"] == 1

    stats = registry.cache_stats()
    assert stats["hits"] == 1
    assert stats["misses"] == 3
    assert stats["evictions"] == 2
    assert stats["cached"] == 1


def test_replace_invalidates_resource_cache(tmp_path: Path):
    (tmp_path / "data.json").write_text('{"value": 1}', encoding="utf-8")
    registry = ResourceRegistry(tmp_path)
    registry.register("data", "data.json", "json")
    assert registry.load_json("data")["value"] == 1

    (tmp_path / "data2.json").write_text('{"value": 2}', encoding="utf-8")
    registry.register("data", "data2.json", "json", replace=True)
    assert registry.load_json("data")["value"] == 2
