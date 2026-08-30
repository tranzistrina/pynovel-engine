from pathlib import Path

from vnengine.asset_runtime import AssetRuntime
from vnengine.resources import ResourceRegistry


class FakeLoader:
    def __init__(self):
        self.calls = []

    def image(self, path):
        self.calls.append(("image", str(path)))
        return object()

    def sound(self, path):
        self.calls.append(("sound", str(path)))
        return object()


def test_bounded_lru_cache_and_stats(tmp_path: Path):
    resources = ResourceRegistry(tmp_path)
    resources.register("a", "a.png", "image")
    resources.register("b", "b.png", "image")
    loader = FakeLoader()
    assets = AssetRuntime(resources, loader=loader, max_cache=1)

    first = assets.load_image("resource://a")
    assert assets.load_image("resource://a") is first
    assets.load_image("resource://b")
    assets.load_image("resource://a")

    stats = assets.stats()
    assert stats["hits"] == 1
    assert stats["misses"] == 3
    assert stats["evictions"] == 2
    assert stats["cached"] == 1
    assert len(loader.calls) == 3


def test_preload_and_explicit_evict(tmp_path: Path):
    resources = ResourceRegistry(tmp_path)
    resources.register("a", "a.png", "image")
    resources.register("b", "b.png", "image")
    loader = FakeLoader()
    assets = AssetRuntime(resources, loader=loader, max_cache=4)

    assert assets.preload(("resource://a", "resource://b"), "image") == 2
    assert assets.stats()["cached"] == 2
    assert assets.evict("resource://a") is True
    assert assets.stats()["cached"] == 1
    assert assets.evict("resource://a") is False
