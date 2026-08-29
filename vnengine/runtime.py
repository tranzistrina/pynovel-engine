from __future__ import annotations
from pathlib import Path
import pygame
from vnengine.script.parser import VNParser
from vnengine.extensions.runtime import ExtensibleRuntime as Runtime
from vnengine.render.display import Renderer
from vnengine.ui.menu import GameMenu
from vnengine.ui.title_screen import TitleScreen
from vnengine.ui.profile import ProfileStore
from vnengine.ui.layout import UIDocument
from vnengine.localization.catalog import Catalog

class Game:
    def __init__(self, project: str | Path):
        self.project=Path(project); lang="ru"; cfg=self.project/"project.json"
        if cfg.exists():
            try:
                import json; lang=json.loads(cfg.read_text(encoding="utf-8")).get("default_language",lang)
            except (OSError,ValueError): pass
        self.profile_store=ProfileStore(self.project); self.profile=self.profile_store.load(); lang=self.profile.language or lang
        self.catalog=Catalog(self.project/"locales",lang)
        self.runtime=Runtime(VNParser().parse_file(self.project/"game.vn"),self.project); self.renderer=Renderer(); self.screen=None
        self.menu=GameMenu(self.project,self.catalog); self.menu.settings.update({"text_speed":self.profile.text_speed,"volume":self.profile.volume})
        self.title=TitleScreen(self.project,self.catalog); self.at_title=True
        self.ui=None; ui_path=self.project/"ui.json"
        if ui_path.exists():
            try:self.ui=UIDocument.load(ui_path,self.project/"theme.json")
            except (OSError,ValueError,TypeError):self.ui=None

    def _apply_profile(self):
        s=self.runtime.state; s.settings["text_speed"]=self.profile.text_speed; s.settings["volume"]=self.profile.volume; s.settings["fullscreen"]=self.profile.fullscreen
    def _save_profile(self):
        self.profile.text_speed=int(self.menu.settings["text_speed"]); self.profile.volume=float(self.menu.settings["volume"]); self.profile_store.save(self.profile)
    def _toggle_fullscreen(self):
        s=self.runtime.state; s.settings["fullscreen"]=not s.settings.get("fullscreen",False); self.profile.fullscreen=s.settings["fullscreen"]; self._save_profile(); self.screen=pygame.display.set_mode((0,0),pygame.FULLSCREEN) if s.settings["fullscreen"] else pygame.display.set_mode((1280,720),pygame.RESIZABLE)
    def _new_game(self):
        self.runtime=Runtime(VNParser().parse_file(self.project/"game.vn"),self.project); self._apply_profile(); self.runtime.apply_scene_manifest(); self.runtime.advance(); self.at_title=False
    def _save_slot(self,slot): self.runtime.save(self.project/"saves"/f"save{slot}.json")
    def _load_slot(self,slot):
        path=self.project/"saves"/f"save{slot}.json"
        if path.exists():self.runtime.load(path); self.at_title=False
    def _handle_ui_action(self,action:str):
        actions={"new_game":"new_game","continue":"continue","menu":"menu","quit":"quit","open_menu":"menu"}
        action=actions.get(action,action)
        if action=="new_game":self._new_game()
        elif action=="continue":self._load_slot(1)
        elif action=="menu":self.menu.open()
        elif action=="quit":self.runtime.state.running=False
        elif action.startswith("jump:"):
            self.runtime._jump(__import__('vnengine.core.model',fromlist=['Action']).Action('jump',{'target':action.split(':',1)[1]}))
    def _handle_menu_result(self,result):
        if not result:return
        if result.action=="quit":self.runtime.state.running=False
        elif result.action=="new_game":self._new_game()
        elif result.action=="main_menu":self.at_title=True; self.title=TitleScreen(self.project,self.catalog); self.title.active=True
        elif result.action=="slot": self._load_slot(result.slot) if getattr(self.menu,"slot_action","save")=="load" else self._save_slot(result.slot)
        elif result.action=="fullscreen":self._toggle_fullscreen()
    def _handle_title_result(self,result):
        if not result:return
        if result.action=="quit":self.runtime.state.running=False
        elif result.action=="new_game":self._new_game()
        elif result.action=="continue":self._load_slot(result.slot or 1)
        elif result.action=="load":self.menu.open(); self.menu.slot_action="load"; self.menu._set_mode("load_slots"); self.at_title=False
        elif result.action=="settings":self.menu.open(); self.menu._set_mode("settings"); self.at_title=False
    def _handle_key(self,key):
        if self.at_title:self._handle_title_result(self.title.handle_key(key)); return
        if self.menu.is_open:self._handle_menu_result(self.menu.handle_key(key)); return
        s=self.runtime.state
        if key==pygame.K_ESCAPE:self.menu.open(); return
        if key in (pygame.K_RETURN,pygame.K_SPACE):
            if s.choice_options:self.runtime.choose(0)
            elif s.dialogue and s.text_progress<len(s.dialogue[1]):s.text_progress=len(s.dialogue[1])
            else:self.runtime.advance()
        elif pygame.K_1<=key<=pygame.K_9 and s.choice_options:
            n=key-pygame.K_1
            if n<len(s.choice_options):self.runtime.choose(n)
        elif key==pygame.K_F5:self._save_slot(1)
        elif key==pygame.K_F9:self._load_slot(1)
        elif key==pygame.K_F8:s.auto_mode=not s.auto_mode
        elif key==pygame.K_F7:s.skip_mode=not s.skip_mode
        elif key==pygame.K_F11:self._toggle_fullscreen()
    def run(self):
        pygame.init()
        try:pygame.mixer.init()
        except pygame.error:pass
        self._apply_profile(); self.screen=pygame.display.set_mode((1280,720),pygame.RESIZABLE); pygame.display.set_caption(self.runtime.state.story.title); clock=pygame.time.Clock()
        while self.runtime.state.running:
            for event in pygame.event.get():
                if event.type==pygame.QUIT:self.runtime.state.running=False
                elif event.type==pygame.KEYDOWN:
                    if not self.runtime.dispatch_input(event): self._handle_key(event.key)
                elif event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
                    if self.at_title:self._handle_title_result(self.title.handle_mouse(event.pos,self.screen.get_size()))
                    elif self.menu.is_open:self._handle_menu_result(self.menu.handle_mouse(event.pos,self.screen.get_size()))
                    elif self.ui:
                        action=self.ui.click(event.pos,self.screen)
                        if action:self._handle_ui_action(action)
                    else:
                        s=self.runtime.state
                        if s.choice_options:
                            idx=self.renderer.choice_at(event.pos,s)
                            if idx is not None:self.runtime.choose(idx)
                        elif s.dialogue:
                            if s.text_progress<len(s.dialogue[1]):s.text_progress=len(s.dialogue[1])
                            else:self.runtime.advance()
            if not self.at_title:
                s=self.runtime.state; dt=max(0.0,clock.get_time()/1000.0); self.runtime.update(dt); s.settings["text_speed"]=float(self.menu.settings.get("text_speed",42)); s.settings["volume"]=float(self.menu.settings.get("volume",0.8))
                if self.ui:self.ui.update(pygame.mouse.get_pos(),self.screen,s)
                if s.dialogue:s.text_progress=min(len(s.dialogue[1]),s.text_progress+s.settings["text_speed"]/60.0)
                if s.auto_mode and s.dialogue and s.text_progress>=len(s.dialogue[1]) and not self.menu.is_open:self.runtime.advance()
                if s.skip_mode and not s.choice_options and not s.dialogue and not self.menu.is_open:self.runtime.advance()
                self.renderer.draw(self.screen,s)
                if self.ui:self.ui.draw(self.screen)
                if self.menu.is_open:self.menu.draw(self.screen,s.history)
                self.runtime.scene_stack.draw(self.screen)
            else:self.title.draw(self.screen)
            pygame.display.flip(); clock.tick(60)
        self.runtime.shutdown(); self._save_profile(); pygame.quit()
