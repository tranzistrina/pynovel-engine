from __future__ import annotations

from typing import Any

from .game_logic import GameLogic


class DeclarativeScene:
    """JSON-defined scene runtime with branching, state and deterministic actions."""

    def __init__(self, definition: dict[str, Any], runtime: Any):
        self.definition = definition
        self.runtime = runtime
        self.actions = list(definition.get("actions", []))
        self.labels = {str(action["label"]): index for index, action in enumerate(self.actions) if isinstance(action, dict) and action.get("type") == "label" and action.get("label")}
        self.index = 0
        self.selected_choice = 0
        self.last_text = ""
        self.last_speaker = ""
        self.logic = GameLogic()
        self.pygame = getattr(getattr(runtime, "frontend", None), "_pygame", None)

    def enter(self) -> None:
        self._refresh_until_visible()

    def exit(self) -> None: pass
    def pause(self) -> None: pass
    def resume(self) -> None: self._refresh_until_visible()
    def update(self, dt: float) -> None: pass

    def _refresh_until_visible(self) -> None:
        guard = 0
        while 0 <= self.index < len(self.actions) and guard < len(self.actions) + 1:
            action = self.actions[self.index]
            kind = action.get("type") if isinstance(action, dict) else None
            if kind == "label":
                self.index += 1
            elif kind in {"set", "change", "emit", "if", "goto"}:
                self._execute_action(action)
            else:
                self._refresh_action()
                return
            guard += 1
        self.last_speaker = ""
        self.last_text = ""

    def _refresh_action(self) -> None:
        action = self.actions[self.index] if 0 <= self.index < len(self.actions) else {}
        if action.get("type") == "say":
            self.last_speaker = str(action.get("speaker", ""))
            self.last_text = str(action.get("text", ""))
        else:
            self.last_speaker = ""
            self.last_text = ""

    def _choices(self) -> list[tuple[int, dict[str, Any]]]:
        return [(i, action) for i, action in enumerate(self.actions) if action.get("type") == "choice" and self._choice_visible(action)]

    def _choice_visible(self, action: dict[str, Any]) -> bool:
        condition = action.get("condition")
        return True if condition is None else self.logic.check(condition)

    def _advance(self) -> bool:
        if not self.actions or not (0 <= self.index < len(self.actions)): return False
        action = self.actions[self.index]
        if action.get("type") == "choice": return True
        self.index += 1
        self._refresh_until_visible()
        return 0 <= self.index < len(self.actions)

    def _execute_action(self, action: dict[str, Any]) -> None:
        kind = action.get("type")
        if kind == "goto":
            target = str(action.get("target", ""))
            if target not in self.labels: raise ValueError(f"Unknown scene label: {target}")
            self.index = self.labels[target]
            return
        self.logic.execute(action)
        self.index += 1
        if kind == "if":
            branch = action.get("then", []) if self.logic.check(action.get("condition", {})) else action.get("else", [])
            for nested in branch: self.logic.execute(nested)

    def _choose(self, choices: list[tuple[int, dict[str, Any]]], number: int) -> bool:
        if number < 0 or number >= len(choices): return False
        _, choice = choices[number]
        self.logic.events.append({"type": "choice", "index": number, "text": choice.get("text", "")})
        target = choice.get("target")
        if target:
            target = str(target)
            if target in self.labels:
                self.index = self.labels[target]
                self._refresh_until_visible()
            else:
                self.runtime.switch_scene(target)
        else:
            self.index += 1
            self._refresh_until_visible()
        return True

    def handle_input(self, event: Any) -> bool:
        if self.pygame is None: return False
        if event.type == self.pygame.KEYDOWN:
            if event.key in (self.pygame.K_SPACE, self.pygame.K_RETURN): return self._advance()
            choices = self._choices()
            if event.key == self.pygame.K_UP: self.selected_choice = max(0, self.selected_choice - 1); return True
            if event.key == self.pygame.K_DOWN: self.selected_choice = min(max(0, len(choices) - 1), self.selected_choice + 1); return True
            number_keys = [getattr(self.pygame, f"K_{n}", None) for n in range(1, 6)]
            if event.key in number_keys: return self._choose(choices, number_keys.index(event.key))
        if event.type == self.pygame.MOUSEBUTTONDOWN and event.button == 1:
            choices = self._choices()
            return self._choose(choices, self.selected_choice) if choices else self._advance()
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
        for visible_index, (_, choice) in enumerate(self._choices()):
            prefix = "> " if visible_index == self.selected_choice else "  "
            text = f"{prefix}{visible_index + 1}. {choice.get('text', '')}"
            target.blit(body_font.render(text, True, (255, 255, 255)), (60, 60 + visible_index * 36))

    def serialize(self) -> dict[str, Any]:
        return {"index": self.index, "selected_choice": self.selected_choice, "speaker": self.last_speaker, "text": self.last_text, "logic": self.logic.serialize()}

    def deserialize(self, payload: dict[str, Any]) -> None:
        self.index = max(0, min(int(payload.get("index", 0)), len(self.actions)))
        self.selected_choice = max(0, int(payload.get("selected_choice", 0)))
        self.last_speaker = str(payload.get("speaker", "")); self.last_text = str(payload.get("text", ""))
        self.logic.deserialize(payload.get("logic", {}))
