from pathlib import Path
from vnengine.project import ProjectLoader


def test_project_loader_reads_manifest_and_map():
    root = Path(__file__).parents[1] / "examples" / "data"
    project = ProjectLoader(root)
    assert project.manifest.name == "Playable Map Demo"
    assert project.manifest.start_scene == "map"
    game_map = project.load_map()
    assert game_map.world.entities.require("army_1").node_id == "capital"
