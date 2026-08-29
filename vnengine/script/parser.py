from __future__ import annotations
import shlex
from pathlib import Path
from vnengine.core.model import Action, ChoiceOption, Story

class VNParseError(ValueError):
    pass

class VNParser:
    """Parser for the human-readable .vn scripting language."""
    ASSIGNMENTS = {"=", "+=", "-=", "*=", "/="}

    def parse_file(self, path: str | Path) -> Story:
        p = Path(path)
        return self.parse(p.read_text(encoding="utf-8"), title=p.stem)

    def parse(self, text: str, title: str = "PyNovel Game") -> Story:
        actions: list[Action] = []
        labels: dict[str, int] = {}
        lines = text.splitlines()
        i = 0
        while i < len(lines):
            raw = lines[i].strip(); line_no = i + 1; i += 1
            if not raw or raw.startswith("#"):
                continue
            try:
                parts = shlex.split(raw)
            except ValueError as exc:
                raise VNParseError(f"Line {line_no}: {exc}") from exc
            cmd = parts[0]
            try:
                if cmd == "title" and len(parts) >= 2:
                    title = " ".join(parts[1:])
                elif cmd == "label" and len(parts) == 2:
                    if parts[1] in labels:
                        raise VNParseError(f"Line {line_no}: duplicate label '{parts[1]}'")
                    labels[parts[1]] = len(actions)
                elif cmd == "scene" and len(parts) >= 2:
                    actions.append(Action("scene", {"name": " ".join(parts[1:])}))
                elif cmd == "background" and len(parts) == 2:
                    actions.append(Action("background", {"path": parts[1]}))
                elif cmd == "character" and len(parts) >= 3:
                    actions.append(Action("character", {"name": parts[1], "image": parts[2], "position": parts[3] if len(parts) > 3 else "center", "expression": parts[4] if len(parts) > 4 else "neutral", "action": "show"}))
                elif cmd == "expression" and len(parts) >= 3:
                    actions.append(Action("expression", {"name": parts[1], "expression": " ".join(parts[2:])}))
                elif cmd == "move" and len(parts) >= 3:
                    actions.append(Action("move", {"name": parts[1], "position": parts[2], "duration": float(parts[3]) if len(parts) > 3 else 0.35}))
                elif cmd == "scale" and len(parts) >= 3:
                    actions.append(Action("scale", {"name": parts[1], "scale": float(parts[2]), "duration": float(parts[3]) if len(parts) > 3 else 0.35}))
                elif cmd == "rotate" and len(parts) >= 3:
                    actions.append(Action("rotate", {"name": parts[1], "rotation": float(parts[2]), "duration": float(parts[3]) if len(parts) > 3 else 0.35}))
                elif cmd == "play_animation" and len(parts) == 2:
                    actions.append(Action("play_animation", {"name": parts[1]}))
                elif cmd == "animation" and len(parts) >= 2:
                    actions.append(Action("play_animation", {"name": parts[1]}))
                elif cmd == "stop_animation" and len(parts) == 2:
                    actions.append(Action("stop_animation", {"name": parts[1]}))
                elif cmd == "hide" and len(parts) == 2:
                    actions.append(Action("character", {"name": parts[1], "action": "hide"}))
                elif cmd == "music" and len(parts) == 2:
                    actions.append(Action("music", {"path": parts[1]}))
                elif cmd == "music_stop" and len(parts) == 1:
                    actions.append(Action("music_stop"))
                elif cmd == "sound" and len(parts) == 2:
                    actions.append(Action("sound", {"path": parts[1]}))
                elif cmd == "say" and len(parts) >= 3:
                    actions.append(Action("say", {"speaker": parts[1], "text": " ".join(parts[2:])}))
                elif cmd == "narrate" and len(parts) >= 2:
                    actions.append(Action("say", {"speaker": "", "text": " ".join(parts[1:])}))
                elif cmd == "set" and len(parts) >= 4 and parts[2] in self.ASSIGNMENTS:
                    actions.append(Action("set", {"name": parts[1], "operator": parts[2], "expression": " ".join(parts[3:])}))
                elif cmd == "jump" and len(parts) == 2:
                    actions.append(Action("jump", {"target": parts[1]}))
                elif cmd == "if" and len(parts) >= 2:
                    actions.append(Action("if", {"expression": " ".join(parts[1:])}))
                elif cmd == "else" and len(parts) == 1:
                    actions.append(Action("else"))
                elif cmd == "endif" and len(parts) == 1:
                    actions.append(Action("endif"))
                elif cmd == "wait" and len(parts) == 2:
                    actions.append(Action("wait", {"seconds": float(parts[1])}))
                elif cmd == "transition" and len(parts) >= 2:
                    actions.append(Action("transition", {"name": parts[1], "duration": float(parts[2]) if len(parts) > 2 else 0.35}))
                elif cmd == "choice":
                    actions.append(Action("choice", {"options": self._parse_choices(lines, i)}))
                    while i < len(lines) and (not lines[i].strip() or lines[i].strip().startswith(('"', "'"))):
                        i += 1
                elif cmd == "end" and len(parts) == 1:
                    actions.append(Action("end"))
                else:
                    raise VNParseError(f"Line {line_no}: unknown or malformed command: {raw}")
            except VNParseError:
                raise
            except (IndexError, TypeError, ValueError) as exc:
                raise VNParseError(f"Line {line_no}: {raw}") from exc
        return Story(actions=actions, labels=labels, title=title)

    def _parse_choices(self, lines: list[str], start: int) -> list[ChoiceOption]:
        options: list[ChoiceOption] = []
        i = start
        while i < len(lines):
            sub = lines[i].strip()
            if not sub:
                i += 1
                continue
            if not sub.startswith(('"', "'")):
                break
            if ":" not in sub:
                raise VNParseError(f"Line {i+1}: choice must be: \"Text\": target")
            left, right = sub.rsplit(":", 1)
            quoted = shlex.split(left.strip()); target = right.strip()
            if len(quoted) != 1 or not target:
                raise VNParseError(f"Line {i+1}: invalid choice")
            options.append(ChoiceOption(quoted[0], target)); i += 1
        if not options:
            raise VNParseError(f"Line {start}: choice requires options")
        return options
