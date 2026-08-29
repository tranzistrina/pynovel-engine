from __future__ import annotations
from pathlib import Path
import pygame
from vnengine.script.parser import VNParser
from vnengine.core.engine import Runtime
from vnengine.render.display import Renderer

class Game:
    def __init__(self, project: str | Path):
        self.project = Path(project)
        self.scenario = self.project / "game.vn"
        self.runtime = Runtime(VNParser().parse_file(self.scenario), self.project)
        self.renderer = Renderer()

    def run(self):
        pygame.init()
        try:
            pygame.mixer.init()
        except pygame.error:
            pass
        screen = pygame.display.set_mode((1280,720), pygame.RESIZABLE)
        pygame.display.set_caption(self.runtime.state.story.title)
        clock = pygame.time.Clock()
        self.runtime.advance()
        running = True
        while running and self.runtime.state.running:
            for e in pygame.event.get():
                if e.type == pygame.QUIT: running = False
                elif e.type == pygame.KEYDOWN:
                    if e.key in (pygame.K_RETURN, pygame.K_SPACE):
                        if self.runtime.state.choice_options: self.runtime.choose(0)
                        else: self.runtime.advance()
                    elif pygame.K_1 <= e.key <= pygame.K_9 and self.runtime.state.choice_options:
                        n = e.key - pygame.K_1
                        if n < len(self.runtime.state.choice_options): self.runtime.choose(n)
                    elif e.key == pygame.K_F5: self.runtime.save(self.project / "save1.json")
                    elif e.key == pygame.K_F9:
                        try: self.runtime.load(self.project / "save1.json")
                        except FileNotFoundError: pass
            self.renderer.draw(screen, self.runtime.state)
            pygame.display.flip(); clock.tick(60)
        pygame.quit()
