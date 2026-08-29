from __future__ import annotations
import pygame
from vnengine.core.engine import GameState

class Renderer:
    def __init__(self):self.font=None; self.small=None; self.title=None
    def _fonts(self):
        if self.font is None:self.font=pygame.font.SysFont('Arial',30); self.small=pygame.font.SysFont('Arial',20); self.title=pygame.font.SysFont('Arial',34,True)
    def _fit(self,surface,rect):
        sw,sh=surface.get_size(); rw,rh=rect.size; scale=min(rw/sw,rh/sh); return pygame.transform.smoothscale(surface,(max(1,int(sw*scale)),max(1,int(sh*scale))))
    def draw(self,screen,state:GameState):
        self._fonts(); w,h=screen.get_size(); screen.fill((18,22,34))
        if state.background:
            img=self._fit(state.background,pygame.Rect(0,0,w,h)); screen.blit(img,img.get_rect(center=(w//2,h//2)))
        else:
            pygame.draw.rect(screen,(35,48,78),(0,0,w,h))
            pygame.draw.circle(screen,(232,207,122),(int(w*.78),int(h*.18)),int(h*.09))
        positions={'left':.23,'center':.50,'right':.77}
        for name,char in state.characters.items():
            surf=state.character_surfaces.get(name)
            if surf is None:
                r=pygame.Rect(0,0,int(w*.28),int(h*.72)); r.midbottom=(int(w*positions.get(char.position,.5)),h-70); pygame.draw.ellipse(screen,(225,185,165),r); pygame.draw.rect(screen,(120,145,195),(r.x+r.w*.2,r.y+r.h*.42,r.w*.6,r.h*.58),border_radius=30); continue
            img=self._fit(surf,pygame.Rect(0,0,w*.42,h*.88)); screen.blit(img,img.get_rect(midbottom=(int(w*positions.get(char.position,.5)),h-70)))
        if state.choice_options:self.draw_choices(screen,state.choice_options)
        elif state.dialogue:self.draw_dialogue(screen,state)
        if state.transition_until>pygame.time.get_ticks()/1000.0:
            overlay=pygame.Surface((w,h),pygame.SRCALPHA); overlay.fill((0,0,0,140)); screen.blit(overlay,(0,0))
    def _wrap(self,text,max_chars=75):
        words=text.split(); out=[]; line=''
        for word in words:
            if len(line)+len(word)+1>max_chars:out.append(line); line=word
            else:line=(line+' '+word).strip()
        if line:out.append(line)
        return out
    def draw_dialogue(self,screen,state):
        w,h=screen.get_size(); box=pygame.Rect(36,h-220,w-72,174); pygame.draw.rect(screen,(12,15,24),box,border_radius=16); pygame.draw.rect(screen,(225,225,235),box,2,border_radius=16)
        speaker,text=state.dialogue; y=box.y+20
        if speaker:screen.blit(self.title.render(speaker,True,(248,218,132)),(box.x+25,y)); y+=42
        shown=text[:int(state.text_progress)]
        for line in self._wrap(shown):screen.blit(self.font.render(line,True,(242,242,246)),(box.x+25,y)); y+=34
        state.text_progress=min(len(text),state.text_progress+0.8)
        screen.blit(self.small.render('Enter/Space continue   F5 save   F9 load   F8 auto   F7 skip',True,(170,178,190)),(box.x+25,box.bottom-30))
    def draw_choices(self,screen,options):
        w,h=screen.get_size(); y=int(h*.33)
        for i,opt in enumerate(options,1):
            r=pygame.Rect(int(w*.17),y,int(w*.66),60); pygame.draw.rect(screen,(18,23,38),r,border_radius=12); pygame.draw.rect(screen,(220,220,230),r,2,border_radius=12); screen.blit(self.font.render(f'{i}. {opt.text}',True,(242,242,246)),(r.x+18,r.y+14)); y+=74
