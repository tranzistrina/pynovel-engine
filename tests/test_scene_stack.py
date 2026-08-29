import pytest
from vnengine.scene_stack import SceneStack


def test_scene_stack_push_pop_and_current():
    stack = SceneStack()
    menu = object(); battle = object()
    stack.push("menu", menu)
    stack.push("battle", battle)
    assert stack.current is battle
    assert stack.current_id == "battle"
    assert stack.ids() == ("menu", "battle")
    assert stack.pop() is battle
    assert stack.current is menu


def test_empty_scene_stack_pop_fails():
    with pytest.raises(IndexError):
        SceneStack().pop()
