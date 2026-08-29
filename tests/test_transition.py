from vnengine.transition import SceneTransition, TransitionManager


def test_transition_progress_and_completion():
    transition = SceneTransition(kind="fade", duration=1.0)
    assert transition.progress == 0.0
    transition.update(0.25)
    assert transition.progress == 0.25
    transition.update(0.75)
    assert transition.finished


def test_transition_manager_clears_finished_transition():
    manager = TransitionManager()
    manager.start("fade", 0.5)
    manager.update(0.5)
    assert not manager.active
    assert manager.update(0.1) == 1.0
