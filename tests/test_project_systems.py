import json
from pathlib import Path

from vnengine.project_document import ProjectDocument
from vnengine.project_runtime import ProjectRuntime


def _project(root: Path) -> None:
    (root / "project.json").write_text(json.dumps({
        "name": "Systems",
        "version": "1.0",
        "map_path": "map.json",
        "start_scene": "map",
        "variables": {},
    }), encoding="utf-8")
    (root / "map.json").write_text(json.dumps({
        "width": 100,
        "height": 100,
        "nodes": [{"id": "start", "x": 0, "y": 0}],
        "connections": [],
        "entities": [{"id": "hero", "node_id": "start", "components": {"transform": {"x": 0}}}],
    }), encoding="utf-8")
    (root / "systems.json").write_text(json.dumps({
        "first": {"kind": "generic", "priority": 10},
        "second": {"kind": "generic", "after": ["first"]},
    }), encoding="utf-8")


def test_project_document_persists_systems(tmp_path):
    document = ProjectDocument(tmp_path)
    document.data.update({"name": "Game", "version": "1", "map_path": "map.json", "start_scene": "map"})
    document.add_system("logic", requires=("transform",), priority=4)
    document.save()
    reloaded = ProjectDocument(tmp_path)
    assert reloaded.data["systems"]["logic"]["priority"] == 4


def test_project_runtime_loads_and_reports_system_plan(tmp_path):
    _project(tmp_path)
    runtime = ProjectRuntime(str(tmp_path), viewport=(0, 0, 100, 100))
    assert runtime.system_plan()["order"] == ["first", "second"]
    runtime.start()
    runtime.update(0.1)
    assert runtime.running is True
