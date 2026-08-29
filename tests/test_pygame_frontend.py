from vnengine.frontends.pygame import PygameFrontend


def test_pygame_frontend_is_lazy():
    frontend = PygameFrontend(width=800, height=600, title="Test", fps=30)
    assert frontend.width == 800
    assert frontend.height == 600
    assert frontend.fps == 30
    assert frontend._pygame is None
    assert frontend.events() == ()
