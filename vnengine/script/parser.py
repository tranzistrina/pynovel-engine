from __future__ import annotations
import shlex
from pathlib import Path
from vnengine.core.model import Action, ChoiceOption, Story

class VNParseError(ValueError):
    pass

class VNParser:
    def parse_file(self, path: str | Path) -> Story:
        p = Path(path)
        return self.parse(p.read_text(encoding="utf-8"), title=p.stem)

    def parse(self, text: str, title: str = "PyNovel Game") -> Story:
        actions: list[Action] = []
        labels: dict[str, int] = {}
        lines = text.splitlines()
        i = 0
        while i < len(lines):
            raw = lines[i].strip()
            i += 1
            if not raw or raw.startswith("#"):
                continue
            try:
                parts = shlex.split(raw)
            except ValueError as exc:
                raise VNParseError(f"Line {i}: {exc}") from exc
            cmd = parts[0]
            if cmd == "label" and len(parts) == 2:
                labels[parts[1]] = len(actions)
            elif cmd == "scene" and len(parts) >= 2:
                actions.append(Action("scene", {"name": " ".join(parts[1:])}))
            elif cmd == "background" and len(parts) == 2:
                actions.append(Action("background", {"path": parts[1]}))
            elif cmd == "character" and len(parts) >= 3:
                actions.append(Action("character", {"name": parts[1], "image": parts[2], "position": parts[3] if len(parts) > 3 else "center"}))
            elif cmd == "music" and len(parts) == 2:
                actions.append(Action("music", {"path": parts[1]}))
            elif cmd == "sound" and len(parts) == 2:
                actions.append(Action("sound", {"path": parts[1]}))
            elif cmd == "say" and len(parts) >= 3:
                actions.append(Action("say", {"speaker": parts[1], "text": " ".join(parts[2:])}))
            elif cmd == "set" and len(parts) >= 4 and parts[2] == "=":
                value = self._value(" ".join(parts[3:]))
                actions.append(Action("set", {"name": parts[1], "value": value}))
            elif cmd == "jump" and len(parts) == 2:
                actions.append(Action("jump", {"target": parts[1]}))
            elif cmd == "choice":
                options: list[ChoiceOption] = []
                while i < len(lines):
                    sub = lines[i].strip()
                    if not sub:
                        i += 1
                        continue
                    if not sub.startswith('"') and not sub.startswith("'"):
                        break
                    if ":" not in sub:
                        raise VNParseError(f"Line {i+1}: choice must be: \"Text\": target")
                    left, right = sub.rsplit(":", 1)
                    quoted = shlex.split(left.strip())
                    target = right.strip()
                    if len(quoted) != 1 or not target:
                        raise VNParseError(f"Line {i+1}: choice must be: \"Text\": target")
                    options.append(ChoiceOption(quoted[0], target))
                    i += 1
                if not options:
                    raise VNParseError(f"Line {i}: choice requires options")
                actions.append(Action("choice", {"options": options}))
            elif cmd == "end":
                actions.append(Action("end"))
            else:
                raise VNParseError(f"Line {i}: unknown or malformed command: {raw}")
        return Story(actions=actions, labels=labels, title=title)

    @staticmethod
    def _value(value: str):
        low = value.lower()
        if low == "true": return True
        if low == "false": return False
        try: return int(value)
        except ValueError: pass
        try: return float(value)
        except ValueError: return value
