from __future__ import annotations
from dataclasses import dataclass, asdict
from pathlib import Path
import json

@dataclass
class PlayerProfile:
    language: str = "ru"
    text_speed: int = 42
    volume: float = 0.8
    fullscreen: bool = False

class ProfileStore:
    def __init__(self, project: str | Path): self.path = Path(project) / "profile.json"
    def load(self) -> PlayerProfile:
        if not self.path.exists(): return PlayerProfile()
        try:
            data=json.loads(self.path.read_text(encoding="utf-8"))
            return PlayerProfile(**{k:data[k] for k in PlayerProfile.__annotations__ if k in data})
        except (OSError, ValueError, TypeError): return PlayerProfile()
    def save(self, profile: PlayerProfile) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(asdict(profile), ensure_ascii=False, indent=2), encoding="utf-8")
