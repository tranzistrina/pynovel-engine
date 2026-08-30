from types import SimpleNamespace

from vnengine.declarative_scene import DeclarativeScene


class FakePygame:
    KEYDOWN = 1
    MOUSEBUTTONDOWN = 2
    K_SPACE = 10
    K_RETURN = 11
    K_UP = 12
    K_DOWN = 13
    K_1 = 20
    K_2 = 21
    K_3 = 22
    K_4 = 23
    K_5 = 24

    class error(Exception): pass


def event(event_type, **kwargs):
    return SimpleNamespace(type=event_type, **kwargs)


def test_declarative_scene_advances_dialogue():
    runtime = SimpleNamespace(frontend=SimpleNamespace(_pygame=FakePygame()))
    scene = DeclarativeScene({"actions": [{"type": "say", "speaker": "hero", "text": "Hello"}, {"type": "say", "speaker": "hero", "text": "World"}]}, runtime)
    scene.enter()
    assert scene.last_text == "Hello"
    assert scene.handle_input(event(FakePygame.KEYDOWN, key=FakePygame.K_SPACE))
    assert scene.last_text == "World"


def test_declarative_scene_choice_switches_scene():
    calls = []
    runtime = SimpleNamespace(frontend=SimpleNamespace(_pygame=FakePygame()), switch_scene=lambda scene_id: calls.append(scene_id))
    scene = DeclarativeScene({"actions": [{"type": "choice", "text": "Forest", "target": "forest"}]}, runtime)
    scene.enter()
    assert scene.handle_input(event(FakePygame.KEYDOWN, key=FakePygame.K_1))
    assert calls == ["forest"]
