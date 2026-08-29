from pathlib import Path
from vnengine.cli import _is_data_project


def test_cli_detects_data_project():
    root = Path(__file__).parents[1] / "examples" / "data"
    assert _is_data_project(root)


def test_cli_keeps_legacy_projects_on_game_runtime(tmp_path):
    assert not _is_data_project(tmp_path)
