from pathlib import Path

import pytest

from vnengine.asset_runtime import AssetRuntime
from vnengine.resources import ResourceRegistry


class Loader:
    def __init__(self): self.calls = []
    def image(self, path): self.calls.append(("image", Path(path).name)); return object()
    def sound(self, path): self.calls.append(("sound", Path(path).name)); return object()
    def font(self, path, size): self.calls.append(("font", Path(path).name, size)); return object()


def test_resource_reference_resolves_and_caches(tmp_path):
    (tmp_path / "hero.png").write_bytes(b"x")
    registry = ResourceRegistry(tmp_path)
    registry.register("hero", "hero.png", "image")
    loader = Loader(); assets = AssetRuntime(registry, loader=loader)
    first = assets.load_image("resource://hero")
    second = assets.load_image("resource://hero")
    assert first is second
    assert loader.calls == [("image", "hero.png")]


def test_asset_runtime_does_not_require_pillow(tmp_path):
    assets = AssetRuntime(ResourceRegistry(tmp_path))
    with pytest.raises(RuntimeError, match="No asset loader configured"):
        assets.load_image("missing.png")
