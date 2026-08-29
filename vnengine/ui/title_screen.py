from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import json
import pygame

@dataclass
class TitleResult:
    action: str
    slot: int | None = None

class TitleScreen:
    def __init__(self, project: str | Path, catalog=None):
        self.project = Path(project); self.catalog = catalog; self.active = True; self.selected = 0
        self.items = ["New Game", "Continue", "Load", "Settings", "Quit"]
        self.font = pygame.font.Font(None, 54); self.small = pygame.font.Font(None, 28)
        self.background = None
        cfg = self.project / "project.json"
        if cfg.exists():
            try:
                data=json.loads(cfg.read_text(encoding="utf-8")); bg=data.get("title_background")
                if bg: self.background=pygame.image.load(str(self.project/bg)).convert()
            except Exception: pass
    def label(self,key,fallback): return self.catalog.get(key,fallback) if self.catalog else fallback
    def handle_key(self,key):
        if key in (pygame.K_UP, pygame.K_w): self.selected=(self.selected-1)%len(self.items)
        elif key in (pygame.K_DOWN, pygame.K_s): self.selected=(self.selected+1)%len(self.items)
        elif key in (pygame.K_RETURN,pygame.K_SPACE): return self.activate()
        return None
    def handle_mouse(self,pos,size):
        w,h=size; top=h*.36
        for i in range(len(self.items)):
            r=pygame.Rect(w*.27,top+i*62,w*.46,48)
            if r.collidepoint(pos): self.selected=i; return self.activate()
        return None
    def activate(self):
        actions=["new_game","continue","load","settings","quit"]
        action=actions[self.selected]
        if action=="continue": return TitleResult("continue",1)
        self.active=False
        return TitleResult(action)
    def draw(self,screen):
        w,h=screen.get_size()
        if self.background:
            bg=pygame.transform.smoothscale(self.background,(w,h)); screen.blit(bg,(0,0))
        else: screen.fill((13,16,28))
        overlay=pygame.Surface((w,h),pygame.SRCALPHA); overlay.fill((0,0,0,105)); screen.blit(overlay,(0,0))
        title=self.label('title','PyNovel'); t=self.font.render(title,True,(255,220,125)); screen.blit(t,t.get_rect(center=(w//2,int(h*.2))))
        top=h*.36
        for i,item in enumerate(self.items):
            r=pygame.Rect(w*.27,top+i*62,w*.46,48)
            if i==self.selected: pygame.draw.rect(screen,(55,70,102),r,border_radius=10)
            text=self.small.render(self.label(item.lower().replace(' ', '_'),item),True,(245,245,250)); screen.blit(text,text.get_rect(center=r.center))
