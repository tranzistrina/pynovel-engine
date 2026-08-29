from __future__ import annotations
import pygame

class Renderer:
    def __init__(self, size=(1280, 720)):
        self.size = size
        self.font = pygame.font.SysFont("Arial", 30)
        self.small = pygame.font.SysFont("Arial", 22)
        self.title = pygame.font.SysFont("Arial", 36, bold=True)

    def _fit(self, surface, rect):
        sw, sh = surface.get_size(); rw, rh = rect.size
        scale = min(rw / sw, rh / sh)
        return pygame.transform.smoothscale(surface, (max(1, int(sw*scale)), max(1, int(sh*scale))))

    def draw(self, screen, state):
        screen.fill((10, 10, 18))
        area = pygame.Rect(0, 0, *screen.get_size())
        if state.background:
            img = self._fit(state.background, area)
            screen.blit(img, img.get_rect(center=area.center))
        w, h = screen.get_size()
        positions = {"left": 0.25, "center": 0.5, "right": 0.75}
        for name, image in state.characters.items():
            img = self._fit(image, pygame.Rect(0, 0, w*0.42, h*0.88))
            x = positions.get(state.character_positions.get(name, "center"), 0.5)*w
            screen.blit(img, img.get_rect(midbottom=(x, h-90)))
        if state.dialogue:
            box = pygame.Rect(40, h-220, w-80, 170)
            pygame.draw.rect(screen, (15, 15, 25), box, border_radius=16)
            pygame.draw.rect(screen, (235, 235, 245), box, 2, border_radius=16)
            speaker, text = state.dialogue
            screen.blit(self.title.render(speaker, True, (245,245,245)), (65, h-195))
            screen.blit(self.font.render(text, True, (230,230,235)), (65, h-145))
            screen.blit(self.small.render("Enter / click to continue", True, (170,170,180)), (65, h-100))
        if state.choice_options:
            self.draw_choices(screen, state.choice_options)

    def draw_choices(self, screen, options):
        w, h = screen.get_size(); y = h*0.35
        for idx, opt in enumerate(options, 1):
            r = pygame.Rect(w*0.2, y, w*0.6, 58)
            pygame.draw.rect(screen, (20,20,32), r, border_radius=12)
            pygame.draw.rect(screen, (220,220,230), r, 2, border_radius=12)
            screen.blit(self.font.render(f"{idx}. {opt.text}", True, (240,240,245)), (r.x+18, r.y+13))
            y += 72
