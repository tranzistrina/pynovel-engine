from __future__ import annotations

from typing import Any


class DeclarativeScene:
    """Minimal JSON-defined scene runtime for AI-generated projects."""

    def __init__(self, definition: dict[str, Any], runtime: Any):
        self.definition = definition
        self.runtime = runtime
        self.actions = list(definition.get("actions", []))
        self.index = 0
        self.selected_choice = 0
        self.last_text = ""
        self.last_speaker = ""
        self.pygame = getattr(getattr(runtime, "frontend", None), "_pygame", None)

    def enter(self) -> None:
        self.index = 0
        self.selected_choice = 0
        self._refresh_action()

    def exit(self) -> None: pass
    def pause(self) -> None: pass
    def resume(self) -> None: pass
    def update(self, dt: float) -> None: pass

    def _refresh_action(self) -> None:
        if 0 <= self.index < len(self.actions):
            action = self.actions[self.index]
            if action.get("type") == "say":
                self.last_speaker = str(action.get("speaker", "")); self.last_text = str(action.get("text", ""))
            else:
                self.last_speaker = ""; self.last_text = ""

    def _choices(self) -> list[dict[str, Any]]:
        return [action for action in self.actions if action.get("type") == "choice"]

    def _advance(self) -> bool:
        if not self.actions: return False
        action = self.actions[self.index]
        if action.get("type") == "choice": return True
        self.index += 1
        if self.index >= len(self.actions):
            return False
        self._refresh_action(); return True

    def handle_input(self, event: Any) -> bool:
        if self.pygame is None: return False
        if event.type == self.pygame.KEYDOWN:
            if event.key in (self.pygame.K_SPACE, self.pygame.K_RETURN): return self._advance()
            if event.key == self.pygame.K_UP: self.selected_choice = max(0, self.selected_choice - 1); return True
            if event.key == self.pygame.K_DOWN: self.selected_choice = min(max(0, len(self._choices()) - 1), self.selected_choice + 1); return True
            if event.key in (self.pygame.K_1, self.pygame.K_2, self.pygame.K_3, self.pygame.K_4, self.pygame.K_5):
                choice_number = event.key - self.pygame.K_1
                choices = self._choices()
                if choice_number < len(choices):
                    target = choices[choice_number].get("target")
                    if target: self.runtime.switch_scene(str(target))
                    return True
        if event.type == self.pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self._advance()
        return False

    def render(self, target: Any) -> None:
        if self.pygame is None: return
        width, height = target.get_size()
        background = self.definition.get("background_color", (24, 24, 32))
        target.fill(tuple(background))
        title_font = self.pygame.font.Font(None, 36)
        body_font = self.pygame.font.Font(None, 30)
        if self.definition.get("background"):
            try:
                image = self.pygame.image.load(self.definition["background"]).convert()
                target.blit(self.pygame.transform.smoothscale(image, (width, height)), (0, 0))
            except (OSError, pygame.error):
                pass
        if self.last_text:
            panel = self.pygame.Surface((width - 80, 190), self.pygame.SRCALPHA); panel.fill((0, 0, 0, 190)); target.blit(panel, (40, height - 220))
            y = height - 200
            if self.last_speaker: target.blit(title_font.render(self.last_speaker, True, (255, 255, 255)), (60, y)); y += 38
            target.blit(body_font.render(self.last_text, True, (255, 255, 255)), (60, y))
        choices = self._choices()
        if choices:
            for i, choice in enumerate(choices):
                prefix = f"{i + 1}. "
                text = prefix + str(choice.get("text", ""))
                target.blit(body_font.render(text, True, (255, 255, 255)), (60, 60 + i * 36))

    def serialize(self) -> dict[str, Any]:
        return {"index": self.index, "selected_choice": self.selected_choice, "speaker": self.last_speaker, "text": self.last_text}

    def deserialize(self, payload: dict[str, Any]) -> None:
        self.index = max(0, min(int(payload.get("index", 0)), len(self.actions)))
        self.selected_choice = max(0, int(payload.get("selected_choice", 0)))
        self.last_speaker = str(payload.get("speaker", "")); self.last_text = str(payload.get("text", ""))
