from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
import json

@dataclass
class Theme:
    background: list[int] | None = None
    panel: list[int] | None = None
    panel_border: list[int] | None = None
    text: list[int] | None = None
    muted_text: list[int] | None = None
    accent: list[int] | None = None
    accent_hover: list[int] | None = None

    def __post_init__(self):
        defaults = {
            "background": [13, 16, 28], "panel": [18, 22, 34],
            "panel_border": [220, 220, 230], "text": [245, 245, 250],
            "muted_text": [165, 170, 185], "accent": [55, 70, 102],
            "accent_hover": [72, 88, 124]
        }
        for key, value in defaults.items():
            if getattr(self, key) is None: setattr(self, key, value)

    @classmethod
    def load(cls, path: str | Path) -> "Theme":
        p = Path(path)
        if not p.exists(): return cls()
        try:
            raw = json.loads(p.read_text(encoding="utf-8"))
            return cls(**{k: raw[k] for k in cls.__annotations__ if k in raw})
        except (OSError, ValueError, TypeError):
            return cls()

    def save(self, path: str | Path) -> None:
        p = Path(path); p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(asdict(self), ensure_ascii=False, indent=2), encoding="utf-8")

    def color(self, name: str) -> tuple[int, int, int]:
        return tuple(getattr(self, name))
