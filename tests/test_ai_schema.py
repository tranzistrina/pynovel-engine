from vnengine.ai_schema import command_schema


def test_command_schema_is_stable_and_machine_readable():
    result = command_schema()
    assert result["api_version"] == 1
    assert result["commands"]["switch_scene"]["required"] == ("scene_id",)
    assert "push_scene" in result["commands"]
