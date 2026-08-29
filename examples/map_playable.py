from __future__ import annotations
import pygame
from vnengine.map import MapDefinition, MapSurface, MapController, MapInteraction, MapInputAdapter, PlayableMap


def build_game() -> tuple[PlayableMap, MapSurface, MapInteraction, MapInputAdapter]:
    definition = MapDefinition.from_dict({
        "width": 1200, "height": 700,
        "nodes": [
            {"id": "capital", "x": 150, "y": 350, "label": "Capital"},
            {"id": "north", "x": 450, "y": 150, "label": "North"},
            {"id": "east", "x": 850, "y": 300, "label": "East"},
            {"id": "south", "x": 500, "y": 550, "label": "South"},
        ],
        "connections": [
            {"source": "capital", "target": "north", "cost": 1}, {"source": "capital", "target": "south", "cost": 1},
            {"source": "north", "target": "east", "cost": 1}, {"source": "south", "target": "east", "cost": 1},
        ],
    })
    game = PlayableMap(definition)
    game.add_entity("army_1", "capital", components={"kind": "army"})
    surface = MapSurface(definition, pygame.Rect(0, 0, 1200, 700))
    controller = MapController(surface)
    interaction = MapInteraction(controller)
    return game, surface, interaction, MapInputAdapter(interaction)


def main() -> None:
    pygame.init(); screen = pygame.display.set_mode((1200, 700)); pygame.display.set_caption("pynovel-engine playable map"); clock = pygame.time.Clock()
    game, surface, interaction, input_adapter = build_game(); running = True
    while running:
        dt = clock.tick(60) / 1000.0; now = pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            elif input_adapter.process(event, now): continue
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: running = False
        game.update(dt)
        screen.fill((25, 25, 30)); surface.draw(screen)
        for entity in game.world.entities.all():
            p = surface.map_to_screen(entity.position); pygame.draw.circle(screen, (230, 80, 80), p, 12)
        pygame.display.flip()
    pygame.quit()


if __name__ == "__main__": main()
