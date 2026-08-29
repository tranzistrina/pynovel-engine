from __future__ import annotations
from pathlib import Path
import pygame
from vnengine.script.parser import VNParser
from vnengine.core.engine import Runtime
from vnengine.render.display import Renderer

class Game:
    def __init__(self,project:str|Path):
        self.project=Path(project); self.runtime=Runtime(VNParser().parse_file(self.project/'game.vn'),self.project); self.renderer=Renderer()
    def run(self):
        pygame.init()
        try: pygame.mixer.init()
        except pygame.error: pass
        screen=pygame.display.set_mode((1280,720),pygame.RESIZABLE); pygame.display.set_caption(self.runtime.state.story.title); clock=pygame.time.Clock(); self.runtime.advance()
        while self.runtime.state.running:
            for e in pygame.event.get():
                if e.type==pygame.QUIT:self.runtime.state.running=False
                elif e.type==pygame.KEYDOWN:
                    if e.key in (pygame.K_RETURN,pygame.K_SPACE):
                        if self.runtime.state.choice_options:self.runtime.choose(0)
                        elif self.runtime.state.dialogue and self.runtime.state.text_progress<len(self.runtime.state.dialogue[1]):self.runtime.state.text_progress=len(self.runtime.state.dialogue[1])
                        else:self.runtime.advance()
                    elif pygame.K_1<=e.key<=pygame.K_9 and self.runtime.state.choice_options:
                        n=e.key-pygame.K_1
                        if n<len(self.runtime.state.choice_options):self.runtime.choose(n)
                    elif e.key==pygame.K_F5:self.runtime.save(self.project/'saves/save1.json')
                    elif e.key==pygame.K_F9:
                        try:self.runtime.load(self.project/'saves/save1.json')
                        except FileNotFoundError:pass
                    elif e.key==pygame.K_F8:self.runtime.state.auto_mode=not self.runtime.state.auto_mode
                    elif e.key==pygame.K_F7:self.runtime.state.skip_mode=not self.runtime.state.skip_mode
                elif e.type==pygame.MOUSEBUTTONDOWN and e.button==1 and self.runtime.state.choice_options:
                    idx=(e.pos[1]-int(screen.get_height()*.33))//74
                    if 0<=idx<len(self.runtime.state.choice_options):self.runtime.choose(idx)
                elif e.type==pygame.MOUSEBUTTONDOWN and e.button==1 and self.runtime.state.dialogue:
                    if self.runtime.state.text_progress<len(self.runtime.state.dialogue[1]):self.runtime.state.text_progress=len(self.runtime.state.dialogue[1])
                    else:self.runtime.advance()
            if self.runtime.state.auto_mode and self.runtime.state.dialogue and self.runtime.state.text_progress>=len(self.runtime.state.dialogue[1]):self.runtime.advance()
            if self.runtime.state.skip_mode and not self.runtime.state.choice_options:self.runtime.advance()
            self.renderer.draw(screen,self.runtime.state); pygame.display.flip(); clock.tick(60)
        pygame.quit()
