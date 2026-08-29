from __future__ import annotations
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any


@dataclass(frozen=True, slots=True)
class ProjectManifest:
    name: str
    version: str = "1.0"
    map_path: str = "map.json"
    start_scene: str = "map"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ProjectManifest":
        return cls(name=str(data["name"]), version=str(data.get("version", "1.0")), map_path=str(data.get("map_path", "map.json")), start_scene=str(data.get("start_scene", "map")))


class ProjectLoader:
    """Loads a self-contained engine project from a directory."""
    def __init__(self, root: str | Path):
        self.root = Path(root).resolve()
        self.manifest = self._load_manifest()

    def _load_manifest(self) -> ProjectManifest:
        path = self.root / "project.json"
        with path.open("r", encoding="utf-8") as handle:
            return ProjectManifest.from_dict(json.load(handle))

    @property
    def map_path(self) -> Path:
        return self.root / self.manifest.map_path

    def load_map(self, **kwargs: Any):
        from .map.loader import load_playable_map
        return load_playable_map(self.map_path, **kwargs)
