from __future__ import annotations

from typing import Any

from .game_logic import GameLogic


class DeclarativeScene:
    """JSON-defined scene runtime with branching, shared state and deterministic actions."""

    def __init__(self, definition: dict[str, Any], runtime: Any):
        self.definition = definition; self.runtime = runtime
        self.actions = list(definition.get("actions", []))
        self.labels = {str(a["label"]): i for i, a in enumerate(self.actions) if isinstance(a, dict) and a.get("type") == "label" and a.get("label")}
        self.index = 0; self.selected_choice = 0; self.last_text = ""; self.last_speaker = ""
        self.logic: GameLogic = getattr(runtime, "logic", GameLogic())
        self.pygame = getattr(getattr(runtime, "frontend", None), "_pygame", None)

    def enter(self) -> None: self.refresh()
    def exit(self) -> None: pass
    def pause(self) -> None: pass
    def resume(self) -> None: self.refresh()
    def update(self, dt: float) -> None: pass

    def refresh(self) -> None:
        guard = 0
        while 0 <= self.index < len(self.actions) and guard <= len(self.actions):
            action = self.actions[self.index]; kind = action.get("type") if isinstance(action, dict) else None
            if kind == "label": self.index += 1
            elif kind in {"set", "change", "emit"}:
                self.logic.execute(action); self.index += 1
            elif kind == "goto": self._goto(action); guard += 1; continue
            elif kind == "if":
                condition = action.get("condition")
                branch = action.get("then", []) if self.logic.check(condition) else action.get("else", [])
                for nested in branch:
                    if isinstance(nested, dict): self.logic.execute(nested)
                self.index += 1
            else:
                self._refresh_action(); return
            guard += 1
        self.last_speaker = ""; self.last_text = ""

    def _goto(self, action: dict[str, Any]) -> None:
        target = str(action.get("target", ""))
        if target in self.labels: self.index = self.labels[target]; return
        if target in self.runtime.scenes.ids(): self.runtime.switch_scene(target); return
        raise ValueError(f"Unknown scene label or scene: {target}")

    def _refresh_action(self) -> None:
        action = self.actions[self.index] if 0 <= self.index < len(self.actions) else {}
        if action.get("type") == "say": self.last_speaker = str(action.get("speaker", "")); self.last_text = str(action.get("text", ""))
        else: self.last_speaker = ""; self.last_text = ""

    def _choices(self) -> list[tuple[int, dict[str, Any]]]:
        return [(i, a) for i, a in enumerate(self.actions) if a.get("type") == "choice" and self.logic.check(a.get("condition"))]

    def _choose(self, number: int) -> bool:
        choices = self._choices()
        if not 0 <= number < len(choices): return False
        action_index, choice = choices[number]; self.logic.events.append({"type": "choice", "index": number, "action_index": action_index, "text": choice.get("text", "")})
        target = choice.get("target")
        if target: self._goto({"target": target})
        else: self.index = action_index + 1; self.refresh()
        return True

    def handle_input(self, event: Any) -> bool:
        if self.pygame is None: return False
        if event.type == self.pygame.KEYDOWN:
            choices = self._choices()
            if event.key in (self.pygame.K_SPACE, self.pygame.K_RETURN): return self._choose(self.selected_choice) if choices else self._advance()
            if event.key == self.pygame.K_UP: self.selected_choice = max(0, self.selected_choice - 1); return True
            if event.key == self.pygame.K_DOWN: self.selected_choice = min(max(0, len(choices) - 1), self.selected_choice + 1); return True
            keys = [getattr(self.pygame, f"K_{n}", None) for n in range(1, 10)]
            if event.key in keys: return self._choose(keys.index(event.key))
        if event.type == self.pygame.MOUSEBUTTONDOWN and event.button == 1:
            choices = self._choices(); return self._choose(self.selected_choice) if choices else self._advance()
        return False

    def _advance(self) -> bool:
        if not (0 <= self.index < len(self.actions)): return False
        if self.actions[self.index].get("type") == "choice": return False
        self.index += 1; self.refresh(); return 0 <= self.index < len(self.actions)

    def render(self, target: Any) -> None:
        if self.pygame is None: return
        width, height = target.get_size(); target.fill(tuple(self.definition.get("background_color", (24, 24, 32))))
        font = self.pygame.font.Font(None, 30); title = self.pygame.font.Font(None, 36)
        background = self.definition.get("background")
        if background:
            try:
                image = self.pygame.image.load(str(background)).convert(); target.blit(self.pygame.transform.smoothscale(image, (width, height)), (0, 0))
            except (OSError, self.pygame.error): pass
        if self.last_text:
            panel = self.pygame.Surface((max(1, width - 80), 190), self.pygame.SRCALPHA); panel.fill((0, 0, 0, 190)); target.blit(panel, (40, height - 220))
            y = height - 200
            if self.last_speaker: target.blit(title.render(self.last_speaker, True, (255, 255, 255)), (60, y)); y += 38
            target.blit(font.render(self.last_text, True, (255, 255, 255)), (60, y))
        for i, (_, choice) in enumerate(self._choices()):
            prefix = "> " if i == self.selected_choice else "  "; target.blit(font.render(f"{prefix}{i + 1}. {choice.get('text', '')}", True, (255, 255, 255)), (60, 60 + i * 36))

    def serialize(self) -> dict[str, Any]: return {"index": self.index, "selected_choice": self.selected_choice, "speaker": self.last_speaker, "text": self.last_text}

    def deserialize(self, payload: dict[str, Any]) -> None:
        self.index = max(0, min(int(payload.get("index", 0)), len(self.actions))); self.selected_choice = max(0, int(payload.get("selected_choice", 0))); self.last_speaker = str(payload.get("speaker", "")); self.last_text = str(payload.get("text", "")); self.refresh()
