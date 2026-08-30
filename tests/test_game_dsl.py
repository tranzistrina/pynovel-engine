from pathlib import Path

import pytest

from vnengine.dsl import DSLParseError, GameDSL
from vnengine.project_document import ProjectDocument


DSL = '''
project "AI Adventure"
version "1.0"
map 1200 700
start main
node town 100 300 "Town"
node forest 500 300 "Forest"
connect town forest
entity hero town
scene main
  background "forest.png"
  character hero
  say hero "We should go."
  choice "Go to forest" -> forest
scene forest
  say hero "We made it."
'''


def test_game_dsl_parses_project_map_and_scenes():
    parsed = GameDSL().parse(DSL)
    assert parsed.project["name"] == "AI Adventure"
    assert parsed.project["start_scene"] == "main"
    assert len(parsed.project["map"]["nodes"]) == 2
    assert len(parsed.scenes["main"]["actions"]) == 3
    assert parsed.scenes["main"]["actions"][2]["target"] == "forest"


def test_game_dsl_compiles_to_project_files(tmp_path):
    result = GameDSL().compile(DSL, tmp_path)
    assert result["scenes"] == ["forest", "main"]
    assert (tmp_path / "project.json").is_file()
    assert (tmp_path / "map.json").is_file()
    assert (tmp_path / "scenes.json").is_file()
    document = ProjectDocument(tmp_path)
    assert len(document.data["scenes"]) == 2
    assert len(document.data["map"]["entities"]) == 1


def test_game_dsl_reports_source_line_for_errors():
    with pytest.raises(DSLParseError) as exc:
        GameDSL().parse('project "Demo"\nscene main\nchoice "broken"')
    assert exc.value.line == 3
