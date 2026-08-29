from __future__ import annotations
from pathlib import Path
from typing import Callable
import json
import operator
import pygame
from vnengine.core.expressions import evaluate
from vnengine.core.model import Action, SaveState, Story, Character

POSITIONS = {"left": 0.23, "center": 0.50, "right": 0.77}

class GameState:
    def __init__(self, story: Story):
        self.story = story; self.index = 0; self.variables = dict(story.variables); self.history = []
        self.background_path = None; self.background = None; self.characters = {}; self.character_surfaces = {}
        self.dialogue = None; self.choice_options = []; self.running = True; self.paused_for_input = False
        self.text_progress = 0.0; self.auto_mode = False; self.skip_mode = False; self.wait_until = 0.0
        self.transition_until = 0.0; self.transition_name = "none"; self.conditional_stack = []
        self.settings = {"text_speed": 42.0, "volume": 0.8, "fullscreen": False}

class Runtime:
    def __init__(self, story: Story, asset_root: str | Path):
        self.state = GameState(story); self.asset_root = Path(asset_root); self._image_cache = {}; self._sound_cache = {}
        self._handlers = {
            "background": self._background, "character": self._character, "music": self._music, "music_stop": self._music_stop,
            "sound": self._sound, "say": self._say, "set": self._set, "jump": self._jump, "if": self._if, "else": self._else,
            "endif": self._endif, "choice": self._choice, "wait": self._wait, "transition": self._transition,
            "end": self._end, "scene": lambda a: None,
        }

    def asset(self, rel: str) -> Path:
        p = Path(rel); return p if p.is_absolute() else self.asset_root / p

    def apply_scene_manifest(self, path: str | Path = "scene.json"):
        manifest = Path(path)
        if not manifest.is_absolute():
            manifest = self.asset_root / manifest
        if not manifest.exists():
            return
        data = json.loads(manifest.read_text(encoding="utf-8"))
        if data.get("background"):
            self._background(Action("background", {"path": data["background"]}))
        for raw in data.get("characters", []):
            self._character(Action("character", {
                "name": raw.get("name", "Character"),
                "image": raw.get("image", ""),
                "position": raw.get("position", "center"),
                "action": "show" if raw.get("visible", True) else "hide",
            }))

    def load_image(self, rel):
        if rel not in self._image_cache: self._image_cache[rel] = pygame.image.load(self.asset(rel)).convert_alpha()
        return self._image_cache[rel]
    def _background(self, a):
        self.state.background_path = a.data["path"]
        try: self.state.background = self.load_image(a.data["path"])
        except (FileNotFoundError, pygame.error): self.state.background = None
    def _character(self, a):
        name = a.data["name"]
        if a.data.get("action") == "hide": self.state.characters.pop(name, None); self.state.character_surfaces.pop(name, None); return
        c = Character(name, a.data["image"], a.data.get("position", "center")); self.state.characters[name] = c
        try: self.state.character_surfaces[name] = self.load_image(c.image)
        except (FileNotFoundError, pygame.error): self.state.character_surfaces.pop(name, None)
    def _music(self, a):
        try:
            pygame.mixer.music.load(self.asset(a.data["path"])); pygame.mixer.music.set_volume(float(self.state.settings["volume"])); pygame.mixer.music.play(-1)
        except pygame.error: pass
    def _music_stop(self, a):
        try: pygame.mixer.music.fadeout(300)
        except pygame.error: pass
    def _sound(self, a):
        try:
            key = a.data["path"]; snd = self._sound_cache.get(key) or pygame.mixer.Sound(self.asset(key)); self._sound_cache[key] = snd
            snd.set_volume(float(self.state.settings["volume"])); snd.play()
        except (pygame.error, FileNotFoundError): pass
    def _say(self, a):
        self.state.dialogue = (a.data["speaker"], a.data["text"]); self.state.history.append(self.state.dialogue); self.state.history = self.state.history[-200:]
        self.state.paused_for_input = True; self.state.text_progress = 0.0
    def _set(self, a):
        name = a.data["name"]; value = evaluate(a.data["expression"], self.state.variables); oper = a.data.get("operator", "=")
        if oper == "=": self.state.variables[name] = value; return
        current = self.state.variables.get(name, 0); funcs = {"+=": operator.add, "-=": operator.sub, "*=": operator.mul, "/=": operator.truediv}
        self.state.variables[name] = funcs[oper](current, value)
    def _jump(self, a):
        self.state.index = self.state.story.labels.get(a.data["target"], len(self.state.story.actions)); self.state.paused_for_input = False; self.state.dialogue = None; self.state.conditional_stack.clear()
    def _if(self, a): self.state.conditional_stack.append(bool(evaluate(a.data["expression"], self.state.variables)))
    def _else(self, a):
        if self.state.conditional_stack: self.state.conditional_stack[-1] = not self.state.conditional_stack[-1]
    def _endif(self, a):
        if self.state.conditional_stack: self.state.conditional_stack.pop()
    def _choice(self, a): self.state.choice_options = a.data["options"]; self.state.paused_for_input = True
    def _wait(self, a): self.state.wait_until = pygame.time.get_ticks() / 1000.0 + float(a.data["seconds"])
    def _transition(self, a):
        self.state.transition_name = a.data["name"]; self.state.transition_until = pygame.time.get_ticks() / 1000.0 + float(a.data.get("duration", .35))
    def _end(self, a): self.state.running = False
    def choose(self, number: int):
        if not 0 <= number < len(self.state.choice_options): return
        target = self.state.choice_options[number].target; self.state.choice_options = []; self._jump(Action("jump", {"target": target})); self.advance()
    def advance(self):
        if not self.state.running: return
        now = pygame.time.get_ticks() / 1000.0
        if self.state.wait_until and now < self.state.wait_until: return
        self.state.wait_until = 0
        if self.state.paused_for_input:
            if self.state.dialogue: self.state.dialogue = None; self.state.paused_for_input = False
            return
        while self.state.index < len(self.state.story.actions) and self.state.running and not self.state.paused_for_input:
            action = self.state.story.actions[self.state.index]; self.state.index += 1
            if self.state.conditional_stack and not all(self.state.conditional_stack) and action.kind not in ("if", "else", "endif"): continue
            self._handlers[action.kind](action)
            if action.kind in ("say", "choice", "end"): break
    def save(self, path: str | Path):
        write = SaveState(self.state.index, self.state.variables, self.state.history, self.state.background_path,
            {k: {"image": v.image, "position": v.position, "visible": v.visible} for k, v in self.state.characters.items()})
        from vnengine.core.save import write_save
        write_save(path, write)
    def load(self, path: str | Path):
        from vnengine.core.save import read_save
        data = read_save(path); s = self.state; s.index = data.action_index; s.variables = data.variables; s.history = data.history
        s.background_path = data.background; s.dialogue = None; s.choice_options = []; s.paused_for_input = False; s.conditional_stack.clear()
        if data.background:
            try: s.background = self.load_image(data.background)
            except (FileNotFoundError, pygame.error): s.background = None
        s.characters = {k: Character(k, v["image"], v.get("position", "center"), v.get("visible", True)) for k, v in data.characters.items()}; s.character_surfaces = {}
        for k, c in s.characters.items():
            try: s.character_surfaces[k] = self.load_image(c.image)
            except (FileNotFoundError, pygame.error): pass
