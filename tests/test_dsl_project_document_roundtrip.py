from pathlib import Path

from vnengine.dsl import GameDSL
from vnengine.project_document import ProjectDocument


def test_compiled_dsl_round_trips_through_project_document(tmp_path):
    text = 'project "Demo"\nmap 800 600\nscene main\n  say hero "Hello"\n'
    GameDSL().compile(text, tmp_path)
    document = ProjectDocument(tmp_path)
    assert document.manifest()["name"] == "Demo"
    assert document.data["scenes"]["main"]["actions"][0]["text"] == "Hello"
    assert document.data["map"]["width"] == 800.0
