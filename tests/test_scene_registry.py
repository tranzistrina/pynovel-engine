import pytest
from vnengine.scene_registry import SceneRegistry


def test_scene_registry_registers_and_creates_scene():
    registry = SceneRegistry()
    registry.register("intro", lambda context: {"id": context.scene_id})
    scene = registry.create("intro", object())
    assert scene == {"id": "intro"}
    assert registry.ids() == ("intro",)


def test_scene_registry_rejects_duplicate_without_replace():
    registry = SceneRegistry()
    registry.register("intro", lambda _: 1)
    with pytest.raises(ValueError):
        registry.register("intro", lambda _: 2)
