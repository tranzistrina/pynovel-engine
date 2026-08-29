from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import StrEnum
from pathlib import Path
import json


class AssetType(StrEnum):
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    FONT = "font"
    DATA = "data"
    SCRIPT = "script"
    OTHER = "other"


_EXTENSIONS: dict[AssetType, set[str]] = {
    AssetType.IMAGE: {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif"},
    AssetType.AUDIO: {".wav", ".ogg", ".mp3", ".flac", ".m4a"},
    AssetType.VIDEO: {".mp4", ".webm", ".mov", ".mkv"},
    AssetType.FONT: {".ttf", ".otf", ".woff", ".woff2"},
    AssetType.DATA: {".json", ".yaml", ".yml", ".toml"},
    AssetType.SCRIPT: {".vn", ".py"},
}


def classify(path: Path) -> AssetType:
    suffix = path.suffix.lower()
    for asset_type, extensions in _EXTENSIONS.items():
        if suffix in extensions:
            return asset_type
    return AssetType.OTHER


@dataclass(frozen=True, slots=True)
class AssetEntry:
    path: str
    asset_type: AssetType
    size: int


class AssetCatalog:
    """Filesystem index for project assets and resource validation."""

    def __init__(self, project: str | Path):
        self.project = Path(project)
        self.entries: list[AssetEntry] = []

    def scan(self) -> list[AssetEntry]:
        root = self.project
        entries: list[AssetEntry] = []
        if not root.exists():
            self.entries = []
            return entries
        for path in sorted(root.rglob("*")):
            if not path.is_file() or any(part.startswith(".") for part in path.relative_to(root).parts):
                continue
            rel = path.relative_to(root).as_posix()
            entries.append(AssetEntry(rel, classify(path), path.stat().st_size))
        self.entries = entries
        return entries

    def by_type(self, asset_type: AssetType) -> list[AssetEntry]:
        return [entry for entry in self.entries if entry.asset_type == asset_type]

    def find(self, path: str) -> AssetEntry | None:
        normalized = Path(path).as_posix()
        return next((entry for entry in self.entries if entry.path == normalized), None)

    def missing(self, references: list[str]) -> list[str]:
        existing = {entry.path for entry in self.entries}
        return [ref.replace("\\", "/") for ref in references if ref.replace("\\", "/") not in existing]

    def write_index(self, destination: str | Path | None = None) -> Path:
        if not self.entries:
            self.scan()
        destination_path = Path(destination) if destination else self.project / ".pynovel" / "assets.json"
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"version": 1, "assets": [asdict(entry) | {"asset_type": entry.asset_type.value} for entry in self.entries]}
        destination_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return destination_path
