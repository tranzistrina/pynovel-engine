from vnengine.game_logic import Condition, GameLogic


def test_logic_set_change_and_conditions():
    logic = GameLogic({"trust": 1})
    logic.set("trust", 2)
    logic.change("gold", 5)
    assert logic.check(Condition("trust", ">=", 2))
    assert logic.get("gold") == 5


def test_logic_conditional_action():
    logic = GameLogic({"has_key": True})
    logic.execute({"type": "if", "condition": {"variable": "has_key", "operator": "==", "value": True}, "then": [{"type": "set", "variable": "door_open", "value": True}]})
    assert logic.get("door_open") is True
