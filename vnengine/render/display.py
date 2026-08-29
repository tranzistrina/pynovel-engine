from __future__ import annotations
import math
import pygame
from vnengine.core.engine import GameState

class Renderer:
    def __init__(self):
        self.font=pygame.font.Font(None,32);self.small=pygame.font.Font(None,24);self.title=pygame.font.Font(None,38);self._texture_cache={}
    def _fit(self,surface,max_w,max_h):
        sw,sh=surface.get_size();scale=min(max_w/sw,max_h/sh);return pygame.transform.smoothscale(surface,(max(1,int(sw*scale)),max(1,int(sh*scale))))
    def _wrap(self,text,width):
        words,lines,current=text.split(),[],""
        for word in words:
            candidate=f"{current} {word}".strip()
            if self.small.size(candidate)[0]<=width:current=candidate
            else:
                if current:lines.append(current)
                current=word
        if current:lines.append(current)
        return lines or [""]
    def _fallback_texture(self,w,h):
        key=(max(1,w//64),max(1,h//64))
        if key in self._texture_cache:
            return pygame.transform.smoothscale(self._texture_cache[key],(w,h))
        surf=pygame.Surface((key[0]*64,key[1]*64))
        surf.fill((18,17,18))
        for y in range(0,surf.get_height(),32):
            pygame.draw.line(surf,(31,27,28),(0,y),(surf.get_width(),y),1)
        for x in range(0,surf.get_width(),64):
            pygame.draw.line(surf,(28,25,26),(x,0),(x,surf.get_height()),1)
        for i in range(55):
            x=(i*97)%surf.get_width();y=(i*53)%surf.get_height();r=2+(i%4);pygame.draw.circle(surf,(40,31,30), (x,y), r)
        self._texture_cache[key]=surf
        return pygame.transform.smoothscale(surf,(w,h))
    def _ornament(self,screen,rect):
        pygame.draw.rect(screen,(77,60,43),rect,2)
        pygame.draw.rect(screen,(30,24,23),rect.inflate(-8,-8),1)
        for x in (rect.left+12,rect.right-12):
            pygame.draw.circle(screen,(117,89,54),(x,rect.top+12),3)
            pygame.draw.circle(screen,(117,89,54),(x,rect.bottom-12),3)
    def draw(self,screen:pygame.Surface,state:GameState):
        w,h=screen.get_size();screen.blit(self._fallback_texture(w,h),(0,0))
        if state.background:
            bg=self._fit(state.background,w,h);screen.blit(bg,bg.get_rect(center=(w//2,h//2)))
        else:
            vignette=pygame.Surface((w,h),pygame.SRCALPHA);vignette.fill((0,0,0,45));screen.blit(vignette,(0,0))
        for name,char in state.characters.items():
            surf=state.character_surfaces.get(name)
            if not surf or not char.visible:continue
            img=self._fit(surf,w*.42*char.scale,h*.86*char.scale)
            if abs(char.rotation)>0.001:img=pygame.transform.rotozoom(img,-char.rotation,1.0)
            if char.opacity<1.0:img=img.copy();img.set_alpha(max(0,min(255,int(char.opacity*255))))
            x=int(w*(char.x/100.0)-img.get_width()/2);y=int(h*(char.y/100.0)-img.get_height());screen.blit(img,(x,y))
        if state.choice_options:self._draw_choices(screen,state)
        elif state.dialogue:self._draw_dialogue(screen,state)
        if state.transition_until>pygame.time.get_ticks()/1000.0:
            overlay=pygame.Surface((w,h),pygame.SRCALPHA);overlay.fill((0,0,0,120));screen.blit(overlay,(0,0))
    def _box(self,screen,rect,alpha=235):
        surf=pygame.Surface(rect.size,pygame.SRCALPHA);surf.fill((8,8,12,alpha));screen.blit(surf,rect);self._ornament(screen,rect)
    def _draw_dialogue(self,screen,state):
        w,h=screen.get_size();rect=pygame.Rect(30,h-205,w-60,175);self._box(screen,rect);speaker,text=state.dialogue
        if speaker:screen.blit(self.title.render(speaker,True,(213,177,105)),(55,rect.y+17))
        visible=text[:int(state.text_progress)];y=rect.y+(58 if speaker else 30)
        for line in self._wrap(visible,rect.width-50)[:3]:screen.blit(self.small.render(line,True,(242,238,225)),(55,y));y+=28
        screen.blit(self.small.render("Enter / Space — продолжить   F5 — сохранить   F9 — загрузить",True,(150,150,155)),(55,rect.bottom-31))
    def _draw_choices(self,screen,state):
        w,h=screen.get_size();total=len(state.choice_options)*64+24;rect=pygame.Rect(max(40,w*.12),max(60,(h-total)/2),min(w-80,w*.76),total);self._box(screen,rect);mx,my=pygame.mouse.get_pos()
        for i,opt in enumerate(state.choice_options):
            btn=pygame.Rect(rect.x+18,rect.y+12+i*64,rect.width-36,52);hovered=btn.collidepoint(mx,my);pygame.draw.rect(screen,(65,48,38) if hovered else (34,30,29),btn,border_radius=8);pygame.draw.rect(screen,(96,73,50),btn,1,border_radius=8);screen.blit(self.small.render(f"{i+1}. {opt.text}",True,(242,238,225)),(btn.x+16,btn.y+14))
    def choice_at(self,pos,state):
        surf=pygame.display.get_surface();w,h=surf.get_size();total=len(state.choice_options)*64+24;rect=pygame.Rect(max(40,w*.12),max(60,(h-total)/2),min(w-80,w*.76),total)
        for i in range(len(state.choice_options)):
            btn=pygame.Rect(rect.x+18,rect.y+12+i*64,rect.width-36,52)
            if btn.collidepoint(pos):return i
        return None
