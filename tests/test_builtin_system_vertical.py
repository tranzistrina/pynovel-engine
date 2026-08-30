from __future__ import annotations

import json

from vnengine.builtin_systems import TransformSystem
from vnengine.project_runtime import ProjectRuntime


class _DummyScene:
    def __init__(self, world):
        self.world = world
    def enter(self): pass
    def exit(self): pass
    def update(self, dt): pass
    def render(self, target): pass


def test_registry_instantiates_builtin_system_by_kind():
    from vnengine.systems import SystemRegistry
    registry = SystemRegistry()
    registry.register_factory("movement", lambda spec: TransformSystem(spec.name, settings=spec.settings))
    registry.register("move", kind="movement", requires=("transform", "velocity"), settings={"scale": 2})
    system = registry.instantiate("move")
    assert isinstance(system, TransformSystem)
    assert system.scale == 2


def test_project_systems_json_creates_and_runs_builtin_movement(tmp_path):
    (tmp_path / "project.json").write_text(json.dumps({
        "name": "vertical", "version": "1.0", "map_path": "map.json", "start_scene": "test", "variables": {}
    }), encoding="utf-8")
    (tmp_path / "map.json").write_text(json.dumps({
        "width": 100, "height": 100,
        "nodes": [{"id": "n", "x": 0, "y": 0}], "connections": [],
        "entities": [{"id": "hero", "node_id": "n", "components": {
            "transform": {"x": 0, "y": 0}, "velocity": {"x": 10, "y": -2}
        }}]
    }), encoding="utf-8")
    (tmp_path / "systems.json").write_text(json.dumps({
        "movement": {"kind": "movement", "requires": ["transform", "velocity"], "phases": ["update"], "enabled": True}
    }), encoding="utf-8")

    from vnengine.project import ProjectLoader
    from vnengine.scene_registry import SceneRegistry
    source_world = ProjectLoader(str(tmp_path)).load_map().world
    scenes = SceneRegistry()
    scenes.register("test", lambda context: _DummyScene(source_world))
    runtime = ProjectRuntime(str(tmp_path), scenes=scenes, viewport=object())
    runtime.start()
    entity = runtime.world.entities.require("hero")
    runtime.update(0.5)
    assert entity.get_component("transform")["x"] == 5
    assert entity.get_component("transform")["y"] == -1


def test_project_systems_are_visible_in_system_plan(tmp_path):
    (tmp_path / "project.json").write_text(json.dumps({"name": "p", "version": "1", "map_path": "map.json", "start_scene": "map"}), encoding="utf-8")
    (tmp_path / "map.json").write_text(json.dumps({"width": 1, "height": 1, "nodes": [], "connections": [], "entities": []}), encoding="utf-8")
    (tmp_path / "systems.json").write_text(json.dumps({"input": {"kind": "input", "phases": ["input"], "events": ["input.raw"]}}), encoding="utf-8")
    runtime = ProjectRuntime(str(tmp_path), viewport=object())
    plan = runtime.system_plan()
    assert plan["order"] == ["input"]
    assert plan["instances"] == ["input"]
