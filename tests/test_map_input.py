from types import SimpleNamespace
import pygame
from vnengine.map.input import MapInputAdapter


class InteractionSpy:
    def __init__(self): self.calls = []
    def begin_pan(self, pos): self.calls.append(("begin_pan", pos))
    def move_pan(self, pos): self.calls.append(("move_pan", pos))
    def end_pan(self): self.calls.append(("end_pan",))
    def pointer_down(self, pos, button, timestamp): self.calls.append(("pointer_down", pos, button, timestamp))


class ControllerSpy:
    def zoom(self, factor, pos): self.calls.append(("zoom", factor, pos))


def test_mouse_input_maps_to_semantic_interaction():
    pygame.init()
    spy = InteractionSpy(); spy.controller = ControllerSpy()
    adapter = MapInputAdapter(spy)
    assert adapter.process(SimpleNamespace(type=pygame.MOUSEBUTTONDOWN, button=1, pos=(10, 20)), 123)
    assert spy.calls[-1] == ("pointer_down", (10, 20), 1, 123)
    assert adapter.process(SimpleNamespace(type=pygame.MOUSEBUTTONDOWN, button=2, pos=(10, 20)), 124)
    assert spy.calls[-1] == ("begin_pan", (10, 20))
    assert adapter.process(SimpleNamespace(type=pygame.MOUSEMOTION, pos=(15, 25)), 125)
    assert spy.calls[-1] == ("move_pan", (15, 25))
    assert adapter.process(SimpleNamespace(type=pygame.MOUSEBUTTONUP, button=2, pos=(15, 25)), 126)
    assert spy.calls[-1] == ("end_pan",)
    pygame.quit()
