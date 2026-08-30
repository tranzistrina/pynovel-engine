import pytest

from vnengine.expression import ExpressionEvaluator, ExpressionError
from vnengine.game_logic import GameLogic


def test_expression_evaluator_supports_safe_game_expressions():
    state = {"score": 12, "trust": 3, "items": ["key"]}
    evaluator = ExpressionEvaluator(state)
    assert evaluator.evaluate("score >= 10 and trust > 2") is True
    assert evaluator.evaluate('has_item("key")') is True
    assert evaluator.evaluate("score + 3 == 15") is True


def test_expression_evaluator_rejects_attribute_and_unknown_calls():
    evaluator = ExpressionEvaluator({"score": 1})
    with pytest.raises(ExpressionError): evaluator.evaluate("__import__('os').system('x')")
    with pytest.raises(ExpressionError): evaluator.evaluate("score.real")


def test_game_logic_tracks_state_and_conditions():
    logic = GameLogic({"score": 5})
    logic.change("score", 3)
    assert logic.get("score") == 8
    assert logic.check({"variable": "score", "operator": ">=", "value": 8}) is True
    assert logic.serialize() == {"variables": {"score": 8}}
