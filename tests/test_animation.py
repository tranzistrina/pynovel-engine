from vnengine.animation.tween import Tween, ease_in_out

def test_ease_bounds():
    assert ease_in_out(0) == 0
    assert ease_in_out(1) == 1

def test_tween_reaches_target():
    tween = Tween(0, 100, 1.0)
    assert tween.step(0.5) == 50.0
    assert not tween.done
    assert tween.step(0.5) == 100.0
    assert tween.done
