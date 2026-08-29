from __future__ import annotations
from pathlib import Path
import pygame
from vnengine.script.parser import VNParser
from vnengine.core.engine import Runtime
from vnengine.render.display import Renderer

class Game:
    def __init__(self, project: str | Path):
        self.project = Path(project); self.runtime = Runtime(VNParser().parse_file(self.project / "game.vn"), self.project); self.renderer = Renderer(); self.screen = None
    def _toggle_fullscreen(self):
        s=self.runtime.state; s.settings['fullscreen']=not s.settings.get('fullscreen',False)
        self.screen=pygame.display.set_mode((0,0),pygame.FULLSCREEN) if s.settings['fullscreen'] else pygame.display.set_mode((1280,720),pygame.RESIZABLE)
    def _handle_key(self,key):
        s=self.runtime.state
        if key==pygame.K_ESCAPE: s.running=False
        elif key in (pygame.K_RETURN,pygame.K_SPACE):
            if s.choice_options:self.runtime.choose(0)
            elif s.dialogue and s.text_progress<len(s.dialogue[1]):s.text_progress=len(s.dialogue[1])
            else:self.runtime.advance()
        elif pygame.K_1<=key<=pygame.K_9 and s.choice_options:
            n=key-pygame.K_1
            if n<len(s.choice_options):self.runtime.choose(n)
        elif key==pygame.K_F5:self.runtime.save(self.project/'saves/save1.json')
        elif key==pygame.K_F9:
            try:self.runtime.load(self.project/'saves/save1.json')
            except (FileNotFoundError,ValueError):pass
        elif key==pygame.K_F8:s.auto_mode=not s.auto_mode
        elif key==pygame.K_F7:s.skip_mode=not s.skip_mode
        elif key==pygame.K_F11:self._toggle_fullscreen()
    def run(self):
        pygame.init()
        try:pygame.mixer.init()
        except pygame.error:pass
        self.screen=pygame.display.set_mode((1280,720),pygame.RESIZABLE); pygame.display.set_caption(self.runtime.state.story.title); clock=pygame.time.Clock()
        self.runtime.apply_scene_manifest(); self.runtime.advance()
        while self.runtime.state.running:
            for e in pygame.event.get():
                if e.type==pygame.QUIT:self.runtime.state.running=False
                elif e.type==pygame.KEYDOWN:self._handle_key(e.key)
                elif e.type==pygame.MOUSEBUTTONDOWN and e.button==1:
                    s=self.runtime.state
                    if s.choice_options:
                        idx=self.renderer.choice_at(e.pos,s)
                        if idx is not None:self.runtime.choose(idx)
                    elif s.dialogue:
                        if s.text_progress<len(s.dialogue[1]):s.text_progress=len(s.dialogue[1])
                        else:self.runtime.advance()
            dt=max(0.0,clock.get_time()/1000.0); s=self.runtime.state; self.runtime.update(dt)
            if s.dialogue:s.text_progress=min(len(s.dialogue[1]),s.text_progress+max(1.0,float(s.settings.get('text_speed',42)))/60.0)
            if s.auto_mode and s.dialogue and s.text_progress>=len(s.dialogue[1]):self.runtime.advance()
            if s.skip_mode and not s.choice_options and not s.dialogue:self.runtime.advance()
            self.renderer.draw(self.screen,s); pygame.display.flip(); clock.tick(60)
        pygame.quit()
