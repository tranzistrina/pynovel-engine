from __future__ import annotations

from pathlib import Path
from typing import Any

from .resources import ResourceRegistry


class AssetRuntime:
    """Frontend-agnostic asset facade with lazy, typed loading and resource:// references."""

    def __init__(self, resources: ResourceRegistry, *, loader: Any = None):
        self.resources = resources
        self.loader = loader
        self._cache: dict[str, Any] = {}

    def resolve(self, reference: str | Path) -> Path:
        value = str(reference)
        if value.startswith("resource://"):
            return self.resources.path(value.removeprefix("resource://"))
        return (self.resources.root / value).resolve()

    def resource_id(self, reference: str | Path) -> str | None:
        value = str(reference)
        return value.removeprefix("resource://") if value.startswith("resource://") else None

    def load_image(self, reference: str | Path) -> Any:
        key = str(reference)
        if key in self._cache: return self._cache[key]
        path = self.resolve(reference)
        if self.loader is None:
            from PIL import Image
            value = Image.open(path)
        else:
            value = self.loader.image(path)
        self._cache[key] = value
        return value

    def load_sound(self, reference: str | Path) -> Any:
        key = str(reference)
        if key in self._cache: return self._cache[key]
        path = self.resolve(reference)
        if self.loader is None: raise RuntimeError("Audio loader is not configured")
        value = self.loader.sound(path)
        self._cache[key] = value
        return value

    def load_font(self, reference: str | Path, size: int) -> Any:
        key = f"{reference}@{int(size)}"
        if key in self._cache: return self._cache[key]
        path = self.resolve(reference)
        if self.loader is None: raise RuntimeError("Font loader is not configured")
        value = self.loader.font(path, int(size))
        self._cache[key] = value
        return value

    def clear(self) -> None: self._cache.clear()

    def inspect(self) -> dict[str, Any]:
        return {"cached": len(self._cache), "resources": self.resources.inspect()}
