from __future__ import annotations
import pygame
from vnengine.map import MapDefinition, MapSurface, MapController, MapInteraction, MapInputAdapter, MapWorld, RouteBuilder, MovementCommand


def build_world() -> MapWorld:
    definition = MapDefinition.from_dict({
        "width": 1200, "height": 700,
        "nodes": [
            {"id": "capital", "x": 150, "y": 350, "label": "Capital"},
            {"id": "north", "x": 450, "y": 150, "label": "North"},
            {"id": "east", "x": 850, "y": 300, "label": "East"},
            {"id": "south", "x": 500, "y": 550, "label": "South"},
        ],
        "connections": [
            {"source": "capital", "target": "north", "cost": 1},
            {"source": "capital", "target": "south", "cost": 1},
            {"source": "north", "target": "east", "cost": 1},
            {"source": "south", "target": "east", "cost": 1},
        ],
    })
    world = MapWorld(definition)
    world.add_entity("army_1", "capital", components={"kind": "army"})
    return world


def main() -> None:
    pygame.init(); screen = pygame.display.set_mode((1200, 700)); pygame.display.set_caption("pynovel-engine map demo"); clock = pygame.time.Clock()
    world = build_world(); surface = MapSurface(world.definition, screen.get_rect()); controller = MapController(surface); interaction = MapInteraction(controller); input_adapter = MapInputAdapter(interaction)
    running = True; font = pygame.font.Font(None, 24)
    while running:
        now = pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            elif input_adapter.process(event, now): continue
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: running = False
        screen.fill((25, 25, 30)); surface.draw(screen)
        for entity in world.entities.all():
            p = surface.map_to_screen(entity.position); pygame.draw.circle(screen, (230, 80, 80), p, 12)
        selected = world.selection.selected
        if selected:
            hint = font.render("LMB: select nodes | MMB: pan | Wheel: zoom | 1/2/3: move selected", True, (240, 240, 240)); screen.blit(hint, (15, 15))
        pygame.display.flip(); world.update(clock.tick(60) / 1000.0)
    pygame.quit()


if __name__ == "__main__": main()
