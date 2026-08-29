from __future__ import annotations
from pathlib import Path
import pygame
from vnengine.script.parser import VNParser
from vnengine.core.engine import Runtime
from vnengine.render.display import Renderer
from vnengine.ui.menu import GameMenu
from vnengine.localization.catalog import Catalog

class Game:
    def __init__(self, project: str | Path):
        self.project = Path(project)
        self.runtime = Runtime(VNParser().parse_file(self.project / "game.vn"), self.project)
        self.renderer = Renderer()
        self.screen = None
        lang = "ru"
        project_cfg = self.project / "project.json"
        if project_cfg.exists():
            try:
                import json
                cfg = json.loads(project_cfg.read_text(encoding="utf-8")); lang = cfg.get("default_language", lang)
            except (OSError, ValueError): pass
        self.catalog = Catalog(self.project / "locales", lang)
        self.menu = GameMenu(self.project, self.catalog)

    def _toggle_fullscreen(self):
        s = self.runtime.state; s.settings["fullscreen"] = not s.settings.get("fullscreen", False)
        self.screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN) if s.settings["fullscreen"] else pygame.display.set_mode((1280,720), pygame.RESIZABLE)

    def _save_slot(self, slot: int): self.runtime.save(self.project / "saves" / f"save{slot}.json")
    def _load_slot(self, slot: int):
        path = self.project / "saves" / f"save{slot}.json"
        if path.exists(): self.runtime.load(path)

    def _handle_menu_result(self, result):
        if result is None: return
        if result.action == "quit": self.runtime.state.running = False
        elif result.action == "slot":
            if getattr(self.menu, "slot_action", "save") == "load": self._load_slot(result.slot)
            else: self._save_slot(result.slot)
        elif result.action == "fullscreen": self._toggle_fullscreen()

    def _handle_key(self, key):
        if self.menu.is_open:
            self._handle_menu_result(self.menu.handle_key(key)); return
        s = self.runtime.state
        if key == pygame.K_ESCAPE: self.menu.open(); return
        if key in (pygame.K_RETURN, pygame.K_SPACE):
            if s.choice_options: self.runtime.choose(0)
            elif s.dialogue and s.text_progress < len(s.dialogue[1]): s.text_progress = len(s.dialogue[1])
            else: self.runtime.advance()
        elif pygame.K_1 <= key <= pygame.K_9 and s.choice_options:
            n = key - pygame.K_1
            if n < len(s.choice_options): self.runtime.choose(n)
        elif key == pygame.K_F5: self._save_slot(1)
        elif key == pygame.K_F9: self._load_slot(1)
        elif key == pygame.K_F8: s.auto_mode = not s.auto_mode
        elif key == pygame.K_F7: s.skip_mode = not s.skip_mode
        elif key == pygame.K_F11: self._toggle_fullscreen()

    def run(self):
        pygame.init()
        try: pygame.mixer.init()
        except pygame.error: pass
        self.screen = pygame.display.set_mode((1280,720), pygame.RESIZABLE)
        pygame.display.set_caption(self.runtime.state.story.title)
        clock = pygame.time.Clock(); self.runtime.apply_scene_manifest(); self.runtime.advance()
        while self.runtime.state.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: self.runtime.state.running = False
                elif event.type == pygame.KEYDOWN: self._handle_key(event.key)
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.menu.is_open:
                        self._handle_menu_result(self.menu.handle_mouse(event.pos, self.screen.get_size()))
                    else:
                        s = self.runtime.state
                        if s.choice_options:
                            idx = self.renderer.choice_at(event.pos, s)
                            if idx is not None: self.runtime.choose(idx)
                        elif s.dialogue:
                            if s.text_progress < len(s.dialogue[1]): s.text_progress = len(s.dialogue[1])
                            else: self.runtime.advance()
            s = self.runtime.state; self.runtime.update(max(0.0, clock.get_time()/1000.0))
            speed = max(1.0, float(self.menu.settings.get("text_speed", 42))); s.settings["text_speed"] = speed; s.settings["volume"] = float(self.menu.settings.get("volume", 0.8))
            if s.dialogue: s.text_progress = min(len(s.dialogue[1]), s.text_progress + speed/60.0)
            if s.auto_mode and s.dialogue and s.text_progress >= len(s.dialogue[1]) and not self.menu.is_open: self.runtime.advance()
            if s.skip_mode and not s.choice_options and not s.dialogue and not self.menu.is_open: self.runtime.advance()
            self.renderer.draw(self.screen, s)
            if self.menu.is_open: self.menu.draw(self.screen, s.history)
            pygame.display.flip(); clock.tick(60)
        pygame.quit()
