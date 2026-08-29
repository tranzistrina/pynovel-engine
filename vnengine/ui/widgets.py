from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable
import pygame
from vnengine.ui.theme import Theme

def _resolve(value: Any, total: int) -> int:
    if isinstance(value, str) and value.endswith('%'):
        return int(total * float(value[:-1]) / 100.0)
    return int(value)

@dataclass
class UIWidget:
    id: str
    x: int | str = 0
    y: int | str = 0
    width: int | str = 100
    height: int | str = 40
    anchor: str = 'top-left'
    z: int = 0
    visible: bool = True
    children: list['UIWidget'] = field(default_factory=list)

    def rect(self, surface: pygame.Surface) -> pygame.Rect:
        sw, sh = surface.get_size(); w, h = _resolve(self.width, sw), _resolve(self.height, sh); x, y = _resolve(self.x, sw), _resolve(self.y, sh)
        if self.anchor == 'center': x -= w // 2; y -= h // 2
        elif self.anchor == 'top-right': x = sw - x - w
        elif self.anchor == 'bottom-left': y = sh - y - h
        elif self.anchor == 'bottom-right': x = sw - x - w; y = sh - y - h
        elif self.anchor == 'bottom-center': x -= w // 2; y = sh - y - h
        elif self.anchor == 'top-center': x -= w // 2
        return pygame.Rect(x, y, w, h)

    def draw(self, surface: pygame.Surface, theme: Theme) -> None:
        if not self.visible: return
        for child in sorted(self.children, key=lambda item: item.z): child.draw(surface, theme)

    def hit_test(self, pos: tuple[int, int], surface: pygame.Surface) -> 'UIWidget | None':
        if not self.visible or not self.rect(surface).collidepoint(pos): return None
        for child in sorted(self.children, key=lambda item: item.z, reverse=True):
            hit = child.hit_test(pos, surface)
            if hit: return hit
        return self

@dataclass
class Panel(UIWidget):
    background: list[int] | None = None; border: list[int] | None = None; border_width: int = 0; radius: int = 0; alpha: int = 255
    def draw(self, surface: pygame.Surface, theme: Theme) -> None:
        if not self.visible: return
        rect = self.rect(surface); layer = pygame.Surface(rect.size, pygame.SRCALPHA); layer.fill(tuple(self.background or theme.panel) + (max(0, min(255, self.alpha)),)); pygame.draw.rect(layer, tuple(self.background or theme.panel) + (max(0, min(255, self.alpha)),), layer.get_rect(), border_radius=self.radius); surface.blit(layer, rect)
        if self.border and self.border_width: pygame.draw.rect(surface, tuple(self.border), rect, self.border_width, border_radius=self.radius)
        for child in sorted(self.children, key=lambda item: item.z): child.draw(surface, theme)

@dataclass
class Label(UIWidget):
    text: str = ''; font_size: int = 28; color: list[int] | None = None; bold: bool = False; align: str = 'left'
    def draw(self, surface: pygame.Surface, theme: Theme) -> None:
        if not self.visible: return
        rect = self.rect(surface); font = pygame.font.Font(None, self.font_size); font.set_bold(self.bold); text = font.render(self.text, True, tuple(self.color or theme.text))
        pos = text.get_rect(center=rect.center) if self.align == 'center' else text.get_rect(midright=rect.midright) if self.align == 'right' else text.get_rect(midleft=rect.midleft); surface.blit(text, pos)
        for child in sorted(self.children, key=lambda item: item.z): child.draw(surface, theme)

@dataclass
class Image(UIWidget):
    path: str = ''; opacity: int = 255; _cache: pygame.Surface | None = field(default=None, init=False, repr=False)
    def draw(self, surface: pygame.Surface, theme: Theme) -> None:
        if not self.visible or not self.path: return
        try:
            if self._cache is None: self._cache = pygame.image.load(self.path).convert_alpha()
            image = pygame.transform.smoothscale(self._cache, self.rect(surface).size); image.set_alpha(max(0, min(255, self.opacity))); surface.blit(image, self.rect(surface))
        except (FileNotFoundError, pygame.error): pass
        for child in sorted(self.children, key=lambda item: item.z): child.draw(surface, theme)

@dataclass
class TextBox(UIWidget):
    text: str = ''; font_size: int = 28; color: list[int] | None = None; padding: int = 14; background: list[int] | None = None; border: list[int] | None = None; border_width: int = 0; radius: int = 10
    def draw(self, surface: pygame.Surface, theme: Theme) -> None:
        if not self.visible: return
        rect = self.rect(surface); layer = pygame.Surface(rect.size, pygame.SRCALPHA); pygame.draw.rect(layer, tuple(self.background or theme.panel) + (230,), layer.get_rect(), border_radius=self.radius); surface.blit(layer, rect)
        if self.border and self.border_width: pygame.draw.rect(surface, tuple(self.border), rect, self.border_width, border_radius=self.radius)
        font = pygame.font.Font(None, self.font_size); lines=[]; line=''
        for word in self.text.split():
            candidate=f'{line} {word}'.strip()
            if font.size(candidate)[0] > rect.width-self.padding*2 and line: lines.append(line); line=word
            else: line=candidate
        if line: lines.append(line)
        y=rect.y+self.padding
        for current in lines: surface.blit(font.render(current,True,tuple(self.color or theme.text)),(rect.x+self.padding,y)); y+=font.get_linesize()
        for child in sorted(self.children, key=lambda item: item.z): child.draw(surface, theme)

@dataclass
class Button(UIWidget):
    text: str = ''; font_size: int = 26; on_click: Callable[[], None] | None = None; background: list[int] | None = None; hover_background: list[int] | None = None; color: list[int] | None = None; radius: int = 10; hovered: bool = False
    def draw(self, surface: pygame.Surface, theme: Theme) -> None:
        if not self.visible: return
        rect=self.rect(surface); bg=self.hover_background if self.hovered and self.hover_background else self.background; bg=bg or (theme.accent_hover if self.hovered else theme.accent); pygame.draw.rect(surface,tuple(bg),rect,border_radius=self.radius); font=pygame.font.Font(None,self.font_size); text=font.render(self.text,True,tuple(self.color or theme.text)); surface.blit(text,text.get_rect(center=rect.center))
    def update_hover(self,pos:tuple[int,int],surface:pygame.Surface)->None: self.hovered=self.visible and self.rect(surface).collidepoint(pos)

WIDGET_TYPES={'panel':Panel,'label':Label,'image':Image,'textbox':TextBox,'button':Button}

def build_widget(data: dict[str, Any], base_path: str | None = None) -> UIWidget:
    kind=str(data.get('type','panel')).lower(); cls=WIDGET_TYPES.get(kind)
    if cls is None: raise ValueError(f'Unknown UI widget type: {kind}')
    payload=dict(data); payload.pop('type',None); children=payload.pop('children',[])
    if 'path' in payload and base_path and not str(payload['path']).startswith('/'):
        from pathlib import Path; payload['path']=str(Path(base_path)/payload['path'])
    widget=cls(**payload); widget.children=[build_widget(item,base_path) for item in children]; return widget
