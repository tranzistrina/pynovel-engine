from __future__ import annotations
import pygame
from vnengine.core.engine import GameState, POSITIONS

class Renderer:
    def __init__(self):
        self.font = pygame.font.Font(None, 32); self.small = pygame.font.Font(None, 24); self.title = pygame.font.Font(None, 38)
    def _fit(self, surface, max_w, max_h):
        sw, sh = surface.get_size(); scale = min(max_w/sw, max_h/sh)
        return pygame.transform.smoothscale(surface, (max(1, int(sw*scale)), max(1, int(sh*scale))))
    def _wrap(self, text, width):
        words, lines, current = text.split(), [], ""
        for word in words:
            candidate = f"{current} {word}".strip()
            if self.small.size(candidate)[0] <= width: current = candidate
            else:
                if current: lines.append(current)
                current = word
        if current: lines.append(current)
        return lines or [""]
    def draw(self, screen: pygame.Surface, state: GameState):
        w, h = screen.get_size(); screen.fill((16, 18, 28))
        if state.background:
            bg = self._fit(state.background, w, h); screen.blit(bg, bg.get_rect(center=(w//2, h//2)))
        for name, char in state.characters.items():
            surf = state.character_surfaces.get(name)
            if not surf: continue
            img = self._fit(surf, w*.42, h*.86); x = int(w*POSITIONS.get(char.position,.5)-img.get_width()/2); y = h-img.get_height(); screen.blit(img, (x,y))
        if state.choice_options: self._draw_choices(screen, state)
        elif state.dialogue: self._draw_dialogue(screen, state)
        if state.transition_until > pygame.time.get_ticks()/1000.0:
            overlay = pygame.Surface((w,h), pygame.SRCALPHA); overlay.fill((0,0,0,120)); screen.blit(overlay,(0,0))
    def _box(self, screen, rect, alpha=225):
        surf = pygame.Surface(rect.size, pygame.SRCALPHA); surf.fill((8,10,18,alpha)); screen.blit(surf,rect); pygame.draw.rect(screen,(215,215,225),rect,2,border_radius=10)
    def _draw_dialogue(self, screen, state):
        w,h=screen.get_size(); rect=pygame.Rect(30,h-200,w-60,170); self._box(screen,rect); speaker,text=state.dialogue
        if speaker: screen.blit(self.title.render(speaker,True,(255,220,120)),(52,rect.y+16))
        visible=text[:int(state.text_progress)]; y=rect.y+(58 if speaker else 28)
        for line in self._wrap(visible,rect.width-45)[:3]: screen.blit(self.small.render(line,True,(245,245,245)),(52,y)); y+=28
        screen.blit(self.small.render("Enter / Space  Continue   F5 Save   F9 Load   F7 Skip   F8 Auto   F11 Fullscreen",True,(165,170,182)),(52,rect.bottom-31))
    def _choice_rect(self, i, screen):
        w,h=screen.get_size(); total=len(self._last_options)*64+24; rect=pygame.Rect(max(40,w*.12),max(60,(h-total)/2),min(w-80,w*.76),total)
        return pygame.Rect(rect.x+18,rect.y+12+i*64,rect.width-36,52), rect
    def _draw_choices(self, screen, state):
        w,h=screen.get_size(); self._last_options=state.choice_options; total=len(state.choice_options)*64+24; rect=pygame.Rect(max(40,w*.12),max(60,(h-total)/2),min(w-80,w*.76),total); self._box(screen,rect)
        mx,my=pygame.mouse.get_pos()
        for i,opt in enumerate(state.choice_options):
            btn=pygame.Rect(rect.x+18,rect.y+12+i*64,rect.width-36,52); hovered=btn.collidepoint(mx,my); pygame.draw.rect(screen,(52,64,92) if hovered else (30,38,58),btn,border_radius=8); screen.blit(self.small.render(f"{i+1}. {opt.text}",True,(245,245,245)),(btn.x+16,btn.y+14))
    def choice_at(self,pos,state):
        w,h=pygame.display.get_surface().get_size(); total=len(state.choice_options)*64+24; rect=pygame.Rect(max(40,w*.12),max(60,(h-total)/2),min(w-80,w*.76),total)
        for i in range(len(state.choice_options)):
            btn=pygame.Rect(rect.x+18,rect.y+12+i*64,rect.width-36,52)
            if btn.collidepoint(pos): return i
        return None
