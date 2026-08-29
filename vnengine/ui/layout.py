from __future__ import annotations
import json
from pathlib import Path
import pygame
from vnengine.ui.theme import Theme
from vnengine.ui.widgets import UIWidget, Button, build_widget
from vnengine.ui.binding import BindingRegistry

class UIDocument:
    def __init__(self, root: UIWidget, theme: Theme | None = None, bindings: BindingRegistry | None = None):
        self.root = root
        self.theme = theme or Theme()
        self.bindings = bindings or BindingRegistry()

    @classmethod
    def load(cls, path: str | Path, theme_path: str | Path | None = None) -> 'UIDocument':
        p = Path(path)
        data = json.loads(p.read_text(encoding='utf-8'))
        theme = Theme.load(theme_path) if theme_path else Theme()
        bindings = BindingRegistry.from_data(data.get('bindings', []))
        root_data = dict(data); root_data.pop('bindings', None)
        return cls(build_widget(root_data, str(p.parent)), theme, bindings)

    def bind(self, state: object) -> list[str]:
        return self.bindings.apply(self, state)

    def update(self, mouse_pos: tuple[int, int], surface: pygame.Surface, state: object | None = None) -> None:
        if state is not None:
            self.bind(state)
        self._update_buttons(self.root, mouse_pos, surface)

    def _update_buttons(self, widget: UIWidget, pos: tuple[int, int], surface: pygame.Surface) -> None:
        if isinstance(widget, Button):
            widget.update_hover(pos, surface)
        for child in widget.children:
            self._update_buttons(child, pos, surface)

    def click(self, pos: tuple[int, int], surface: pygame.Surface) -> str | None:
        widget = self.root.hit_test(pos, surface)
        if isinstance(widget, Button):
            return getattr(widget, 'action', None) or widget.id
        return None

    def find(self, widget_id: str) -> UIWidget | None:
        if self.root.id == widget_id:
            return self.root
        return self._find(self.root, widget_id)

    def _find(self, widget: UIWidget, widget_id: str) -> UIWidget | None:
        for child in widget.children:
            if child.id == widget_id:
                return child
            found = self._find(child, widget_id)
            if found is not None:
                return found
        return None

    def set_visible(self, widget_id: str, visible: bool) -> bool:
        widget = self.find(widget_id)
        if widget is None:
            return False
        widget.visible = visible
        return True

    def draw(self, surface: pygame.Surface) -> None:
        self.root.draw(surface, self.theme)
