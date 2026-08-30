import json
from pathlib import Path

from vnengine.ai_builder import AIProjectBuilder
from vnengine.project_document import ProjectDocument
from vnengine.project_runtime import ProjectRuntime


def test_resources_round_trip_through_project_document(tmp_path: Path):
    doc = ProjectDocument(tmp_path)
    doc.begin()
    doc.add_resource("hero", "assets/hero.png", "image", metadata={"role": "character"})
    doc.commit(); doc.save()
    loaded = ProjectDocument(tmp_path)
    assert loaded.data["resources"]["hero"]["path"] == "assets/hero.png"
    assert json.loads((tmp_path / "resources.json").read_text()) ["hero"]["type"] == "image"


def test_runtime_loads_declared_resources(tmp_path: Path):
    builder = AIProjectBuilder(tmp_path)
    builder.apply([
        {"command": "create_project", "name": "Resource Demo"},
        {"command": "add_resource", "resource_id": "bg", "path": "background.png", "resource_type": "image"},
        {"command": "create_map", "width": 800, "height": 600},
    ])
    runtime = ProjectRuntime(tmp_path, viewport=(0, 0, 800, 600))
    assert runtime.resources.has("bg")
    assert runtime.resources.get("bg").type == "image"
