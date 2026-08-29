from vnengine.core.expressions import evaluate

def test_expression_evaluation():
    env={'affection':5,'trusted':True}
    assert evaluate('affection >= 3',env) is True
    assert evaluate('affection < 3 or trusted',env) is True
    assert evaluate('not trusted',env) is False
    assert evaluate('affection + 2',env) == 7
