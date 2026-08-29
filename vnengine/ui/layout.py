from __future__ import annotations
import json
from pathlib import Path
import pygame
from vnengine.ui.theme import Theme
from vnengine.ui.widgets import UIWidget, Button, build_widget

class UIDocument:
    def __init__(self, root: UIWidget, theme: Theme | None = None): self.root=root; self.theme=theme or Theme()
    @classmethod
    def load(cls, path: str | Path, theme_path: str | Path | None = None) -> 'UIDocument':
        p=Path(path); data=json.loads(p.read_text(encoding='utf-8')); theme=Theme.load(theme_path) if theme_path else Theme(); return cls(build_widget(data, str(p.parent)), theme)
    def update(self, mouse_pos: tuple[int,int], surface: pygame.Surface) -> None: self._update_buttons(self.root,mouse_pos,surface)
    def _update_buttons(self, widget: UIWidget, pos: tuple[int,int], surface: pygame.Surface) -> None:
        if isinstance(widget,Button): widget.update_hover(pos,surface)
        for child in widget.children:self._update_buttons(child,pos,surface)
    def click(self,pos:tuple[int,int],surface:pygame.Surface)->bool:
        widget=self.root.hit_test(pos,surface)
        if isinstance(widget,Button) and widget.on_click: widget.on_click(); return True
        return isinstance(widget,Button)
    def draw(self,surface:pygame.Surface)->None: self.root.draw(surface,self.theme)
