from vnengine.core.model import Action, Story
from vnengine.extensions.runtime import ExtensibleRuntime


def test_registered_command_executes_from_vn_action():
    runtime = ExtensibleRuntime(Story(actions=[Action("custom_action", {"value": 7})]), ".")
    seen = []

    def handler(context):
        seen.append((context.runtime, context.action.data["value"]))

    runtime.register_command("custom_action", handler)
    runtime.advance()

    assert seen == [(runtime, 7)]
    assert "custom_action" in runtime.command_names()


def test_builtin_command_keeps_priority_over_registered_override():
    runtime = ExtensibleRuntime(Story(actions=[Action("emit", {"event": "demo", "args": []})]), ".")
    seen = []
    runtime.subscribe("demo", lambda event: seen.append(event))
    runtime.register_command("emit", lambda context: seen.append("override"))

    runtime.advance()

    assert seen == [{"args": []}]
