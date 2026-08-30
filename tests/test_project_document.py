import json
from vnengine.project_document import ProjectDocument


def test_document_transaction_rolls_back(tmp_path):
    doc = ProjectDocument(tmp_path, data={"name": "Demo", "version": "1.0", "map_path": "map.json", "start_scene": "map"})
    doc.begin()
    doc.add_node("a", 10, 20)
    doc.rollback()
    assert doc.inspect()["map"]["nodes"] == 0


def test_document_batch_changes_save_as_project_files(tmp_path):
    doc = ProjectDocument(tmp_path, data={"name": "Demo", "version": "1.0", "map_path": "map.json", "start_scene": "map"})
    doc.begin()
    doc.ensure_map()
    doc.add_node("a", 0, 0)
    doc.add_node("b", 100, 0)
    doc.add_connection("a", "b")
    doc.add_entity("hero", "a", components={"kind": "character"})
    doc.commit(); doc.save()
    assert json.loads((tmp_path / "project.json").read_text())["name"] == "Demo"
    assert len(json.loads((tmp_path / "map.json").read_text())["nodes"]) == 2
