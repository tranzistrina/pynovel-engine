from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import json
import pygame

@dataclass
class MenuResult:
    action: str
    slot: int | None = None

class GameMenu:
    def __init__(self, project: Path, catalog=None):
        self.project = Path(project); self.catalog = catalog; self.mode = "closed"; self.selected = 0
        self.options = ["Resume", "New Game", "Save", "Load", "History", "Settings", "Main Menu", "Quit"]
        self.slots = list(range(1, 6)); self.settings = {"text_speed": 42, "volume": 0.8}; self._font = self._small = None; self.load_settings()
    def _fonts(self):
        if self._font is None: self._font = pygame.font.Font(None, 36); self._small = pygame.font.Font(None, 26)
    @property
    def is_open(self): return self.mode != "closed"
    def label(self, key: str, fallback: str) -> str: return self.catalog.get(key, fallback) if self.catalog else fallback
    def load_settings(self):
        p=self.project/"settings.json"
        if p.exists():
            try:self.settings.update(json.loads(p.read_text(encoding="utf-8")))
            except (OSError,ValueError):pass
    def save_settings(self):
        (self.project/"settings.json").write_text(json.dumps(self.settings,ensure_ascii=False,indent=2),encoding="utf-8")
    def open(self): self.mode,self.selected="main",0
    def close(self): self.mode="closed"
    def _set_mode(self, mode): self.mode,self.selected=mode,0
    def handle_key(self,key):
        if self.mode=="closed":
            if key==pygame.K_ESCAPE:self.open(); return MenuResult("open")
            return None
        if key==pygame.K_ESCAPE:
            if self.mode=="main":self.close(); return MenuResult("resume")
            self._set_mode("main"); return None
        if key==pygame.K_UP:self.selected=(self.selected-1)%self._count(); return None
        if key==pygame.K_DOWN:self.selected=(self.selected+1)%self._count(); return None
        if key in (pygame.K_RETURN,pygame.K_SPACE):return self.activate()
        if self.mode=="main" and key==pygame.K_s:self.slot_action="save"; self._set_mode("save_slots"); return None
        if self.mode=="main" and key==pygame.K_l:self.slot_action="load"; self._set_mode("load_slots"); return None
        if self.mode=="main" and key==pygame.K_h:self._set_mode("history"); return None
        if self.mode=="main" and key==pygame.K_o:self._set_mode("settings"); return None
        if self.mode in ("save_slots","load_slots") and pygame.K_1<=key<=pygame.K_5:self.selected=key-pygame.K_1; return self.activate()
        if self.mode=="settings" and self.selected==0 and key in (pygame.K_LEFT,pygame.K_RIGHT):self.settings["text_speed"]=max(8,min(120,self.settings["text_speed"]+(8 if key==pygame.K_RIGHT else -8))); self.save_settings(); return None
        if self.mode=="settings" and self.selected==1 and key in (pygame.K_LEFT,pygame.K_RIGHT):self.settings["volume"]=max(0.0,min(1.0,round(self.settings["volume"]+(0.1 if key==pygame.K_RIGHT else -0.1),1))); self.save_settings(); return None
        if self.mode=="settings" and self.selected==2 and key in (pygame.K_LEFT,pygame.K_RIGHT):return MenuResult("fullscreen")
        return None
    def _count(self): return {"main":len(self.options),"save_slots":len(self.slots)+1,"load_slots":len(self.slots)+1,"history":1,"settings":3}.get(self.mode,1)
    def activate(self):
        if self.mode=="main":
            action=["resume","new_game","save_menu","load_menu","history","settings","main_menu","quit"][self.selected]
            if action=="new_game":self.close(); return MenuResult("new_game")
            if action=="save_menu":self.slot_action="save"; self._set_mode("save_slots"); return MenuResult("noop")
            if action=="load_menu":self.slot_action="load"; self._set_mode("load_slots"); return MenuResult("noop")
            if action=="history":self._set_mode("history"); return MenuResult("noop")
            if action=="settings":self._set_mode("settings"); return MenuResult("noop")
            if action=="main_menu":return MenuResult("noop")
            if action=="resume":self.close()
            return MenuResult(action)
        if self.mode in ("save_slots","load_slots"):
            if self.selected==len(self.slots):self._set_mode("main"); return MenuResult("noop")
            return MenuResult("slot",self.slots[self.selected])
        if self.mode=="history":self._set_mode("main"); return MenuResult("noop")
        if self.mode=="settings" and self.selected==2:return MenuResult("fullscreen")
        return MenuResult("noop")
    def handle_mouse(self,pos,size):
        if self.mode=="closed":return None
        w,h=size; px,py=pos; panelx=max(60,w*.18); panelw=min(w-120,w*.64); top=max(50,h*.08)
        if self.mode=="main":
            for i in range(len(self.options)):
                r=pygame.Rect(panelx+22,top+82+i*58,panelw-44,46)
                if r.collidepoint(px,py):self.selected=i; return self.activate()
        if self.mode in ("save_slots","load_slots"):
            for i in range(len(self.slots)+1):
                r=pygame.Rect(panelx+22,top+94+i*58,panelw-44,46)
                if r.collidepoint(px,py):self.selected=i; return self.activate()
        if self.mode=="settings":
            for i in range(3):
                r=pygame.Rect(panelx+22,top+92+i*66,panelw-44,52)
                if r.collidepoint(px,py):self.selected=i; return self.activate()
        return None
    def draw(self,screen,history):
        if self.mode=="closed":return
        self._fonts(); w,h=screen.get_size(); overlay=pygame.Surface((w,h),pygame.SRCALPHA); overlay.fill((0,0,0,185)); screen.blit(overlay,(0,0))
        panel=pygame.Rect(max(60,w*.18),max(50,h*.08),min(w-120,w*.64),min(h-100,h*.84)); pygame.draw.rect(screen,(18,22,34),panel,border_radius=18); pygame.draw.rect(screen,(220,220,230),panel,2,border_radius=18)
        title={"main":"Menu","save_slots":"Save","load_slots":"Load","history":"History","settings":"Settings"}[self.mode]; screen.blit(self._font.render(title,True,(255,220,125)),(panel.x+28,panel.y+22))
        if self.mode=="main":
            for i,text in enumerate(self.options):
                y=panel.y+82+i*58; r=pygame.Rect(panel.x+22,y,panel.width-44,46)
                if i==self.selected:pygame.draw.rect(screen,(55,70,102),r,border_radius=9)
                screen.blit(self._small.render(f"{i+1}. {text}",True,(245,245,250)),(r.x+16,r.y+10))
        elif self.mode in ("save_slots","load_slots"):
            labels=[f"Slot {s}" for s in self.slots]+["Back"]
            for i,text in enumerate(labels):
                y=panel.y+94+i*58; r=pygame.Rect(panel.x+22,y,panel.width-44,46)
                if i==self.selected:pygame.draw.rect(screen,(55,70,102),r,border_radius=9)
                status="saved" if (self.project/"saves"/f"save{i+1}.json").exists() else "empty"; screen.blit(self._small.render(f"{text}  [{status}]",True,(245,245,250)),(r.x+16,r.y+10))
        elif self.mode=="settings":
            rows=[f"Text speed: {self.settings['text_speed']}  (< / >)",f"Volume: {int(self.settings['volume']*100)}%  (< / >)","Toggle fullscreen"]
            for i,text in enumerate(rows):
                y=panel.y+92+i*66; r=pygame.Rect(panel.x+22,y,panel.width-44,52)
                if i==self.selected:pygame.draw.rect(screen,(55,70,102),r,border_radius=9)
                screen.blit(self._small.render(text,True,(245,245,250)),(r.x+16,r.y+13))
        else:
            y=panel.y+84
            for speaker,text in history[-12:]:screen.blit(self._small.render(((speaker+": ") if speaker else "")+text[:100],True,(235,235,242)),(panel.x+24,y)); y+=34
            screen.blit(self._small.render("Esc to return",True,(165,170,185)),(panel.x+24,panel.bottom-34))
