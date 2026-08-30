from __future__ import annotations

from typing import Any


class DeclarativeScene:
    """Minimal JSON-defined scene runtime for AI-generated projects."""

    def __init__(self, definition: dict[str, Any], runtime: Any):
        self.definition = definition; self.runtime = runtime; self.actions = list(definition.get("actions", []))
        self.index = 0; self.selected_choice = 0; self.last_text = ""; self.last_speaker = ""
        self.pygame = getattr(getattr(runtime, "frontend", None), "_pygame", None)

    def enter(self) -> None:
        self.index = 0; self.selected_choice = 0; self._refresh_action()
    def exit(self) -> None: pass
    def pause(self) -> None: pass
    def resume(self) -> None: pass
    def update(self, dt: float) -> None: pass

    def _refresh_action(self) -> None:
        if 0 <= self.index < len(self.actions):
            action = self.actions[self.index]
            if action.get("type") == "say": self.last_speaker = str(action.get("speaker", "")); self.last_text = str(action.get("text", ""))
            else: self.last_speaker = ""; self.last_text = ""

    def _choices(self) -> list[dict[str, Any]]: return [a for a in self.actions if a.get("type") == "choice"]

    def _advance(self) -> bool:
        if not self.actions: return False
        if self.actions[self.index].get("type") == "choice": return True
        self.index += 1
        if self.index >= len(self.actions): return False
        self._refresh_action(); return True

    def handle_input(self, event: Any) -> bool:
        if self.pygame is None: return False
        if event.type == self.pygame.KEYDOWN:
            if event.key in (self.pygame.K_SPACE, self.pygame.K_RETURN): return self._advance()
            if event.key == self.pygame.K_UP: self.selected_choice = max(0, self.selected_choice - 1); return True
            if event.key == self.pygame.K_DOWN: self.selected_choice = min(max(0, len(self._choices()) - 1), self.selected_choice + 1); return True
            number_keys = [getattr(self.pygame, f"K_{n}", None) for n in range(1, 6)]
            if event.key in number_keys:
                number = number_keys.index(event.key); choices = self._choices()
                if number < len(choices):
                    target = choices[number].get("target")
                    if target: self.runtime.switch_scene(str(target))
                    return True
        if event.type == self.pygame.MOUSEBUTTONDOWN and event.button == 1: return self._advance()
        return False

    def render(self, target: Any) -> None:
        if self.pygame is None: return
        width, height = target.get_size(); target.fill(tuple(self.definition.get("background_color", (24, 24, 32))))
        background = self.definition.get("background")
        if background:
            try:
                image = self.pygame.image.load(background).convert(); target.blit(self.pygame.transform.smoothscale(image, (width, height)), (0, 0))
            except (OSError, self.pygame.error): pass
        title_font = self.pygame.font.Font(None, 36); body_font = self.pygame.font.Font(None, 30)
        if self.last_text:
            panel = self.pygame.Surface((max(1, width - 80), 190), self.pygame.SRCALPHA); panel.fill((0, 0, 0, 190)); target.blit(panel, (40, height - 220))
            y = height - 200
            if self.last_speaker: target.blit(title_font.render(self.last_speaker, True, (255, 255, 255)), (60, y)); y += 38
            target.blit(body_font.render(self.last_text, True, (255, 255, 255)), (60, y))
        for i, choice in enumerate(self._choices()): target.blit(body_font.render(f"{i + 1}. {choice.get('text', '')}", True, (255, 255, 255)), (60, 60 + i * 36))

    def serialize(self) -> dict[str, Any]: return {"index": self.index, "selected_choice": self.selected_choice, "speaker": self.last_speaker, "text": self.last_text}

    def deserialize(self, payload: dict[str, Any]) -> None:
        self.index = max(0, min(int(payload.get("index", 0)), len(self.actions))); self.selected_choice = max(0, int(payload.get("selected_choice", 0)))
        self.last_speaker = str(payload.get("speaker", "")); self.last_text = str(payload.get("text", ""))
