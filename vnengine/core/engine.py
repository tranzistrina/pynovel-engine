from __future__ import annotations
import json
from dataclasses import asdict
from pathlib import Path
from typing import Callable
import pygame
from vnengine.core.model import Action, SaveState, Story

class GameState:
    def __init__(self, story: Story):
        self.story = story
        self.index = 0
        self.variables = dict(story.variables)
        self.history: list[tuple[str, str]] = []
        self.background: pygame.Surface | None = None
        self.characters: dict[str, pygame.Surface] = {}
        self.character_positions: dict[str, str] = {}
        self.dialogue: tuple[str, str] | None = None
        self.choice_options = []
        self.running = True
        self.paused_for_input = False
        self.text_progress = 0.0
        self.auto_mode = False
        self.skip_mode = False

class Runtime:
    def __init__(self, story: Story, asset_root: str | Path):
        self.state = GameState(story)
        self.asset_root = Path(asset_root)
        self._image_cache: dict[str, pygame.Surface] = {}
        self._handlers: dict[str, Callable[[Action], None]] = {
            "background": self._background, "character": self._character,
            "music": self._music, "sound": self._sound, "say": self._say,
            "set": self._set, "jump": self._jump, "choice": self._choice,
            "end": self._end, "scene": lambda a: None,
        }

    def asset(self, rel: str) -> Path:
        p = Path(rel)
        return p if p.is_absolute() else self.asset_root / p

    def load_image(self, rel: str):
        key = str(rel)
        if key not in self._image_cache:
            self._image_cache[key] = pygame.image.load(self.asset(rel)).convert_alpha()
        return self._image_cache[key]

    def _background(self, a):
        try: self.state.background = self.load_image(a.data["path"])
        except Exception: self.state.background = None

    def _character(self, a):
        name = a.data["name"]
        try: self.state.characters[name] = self.load_image(a.data["image"])
        except Exception: pass
        self.state.character_positions[name] = a.data["position"]

    def _music(self, a):
        try: pygame.mixer.music.load(self.asset(a.data["path"])); pygame.mixer.music.play(-1)
        except Exception: pass

    def _sound(self, a):
        try: pygame.mixer.Sound(self.asset(a.data["path"])).play()
        except Exception: pass

    def _say(self, a):
        self.state.dialogue = (a.data["speaker"], a.data["text"])
        self.state.history.append(self.state.dialogue)
        self.state.paused_for_input = True
        self.state.text_progress = 0

    def _set(self, a): self.state.variables[a.data["name"]] = a.data["value"]

    def _jump(self, a): self.state.index = self.state.story.labels.get(a.data["target"], len(self.state.story.actions)); self.state.paused_for_input = False

    def _choice(self, a):
        self.state.choice_options = a.data["options"]
        self.state.paused_for_input = True

    def choose(self, number: int):
        target = self.state.choice_options[number].target
        self.state.choice_options = []
        self._jump(Action("jump", {"target": target}))

    def _end(self, a): self.state.running = False

    def advance(self):
        if not self.state.running: return
        if self.state.paused_for_input:
            if self.state.dialogue:
                self.state.dialogue = None
                self.state.paused_for_input = False
            return
        while self.state.index < len(self.state.story.actions) and self.state.running and not self.state.paused_for_input:
            action = self.state.story.actions[self.state.index]
            self.state.index += 1
            self._handlers[action.kind](action)
            if action.kind in ("say", "choice", "end"): break

    def save(self, path: str | Path):
        data = asdict(SaveState(self.state.index, self.state.variables, self.state.history))
        Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def load(self, path: str | Path):
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        self.state.index = data["action_index"]
        self.state.variables = data["variables"]
        self.state.history = [tuple(x) for x in data["history"]]
        self.state.dialogue = None
        self.state.choice_options = []
        self.state.paused_for_input = False
