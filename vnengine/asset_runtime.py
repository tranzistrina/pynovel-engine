from __future__ import annotations

from pathlib import Path
from typing import Any

from .resources import ResourceRegistry


class AssetRuntime:
    """Frontend-agnostic typed asset facade with lazy caching and resource:// references."""

    def __init__(self, resources: ResourceRegistry, *, loader: Any = None):
        self.resources = resources; self.loader = loader; self._cache: dict[str, Any] = {}

    def resolve(self, reference: str | Path) -> Path:
        value = str(reference)
        return self.resources.path(value.removeprefix("resource://")) if value.startswith("resource://") else self.resources._safe_path(value)

    def resource_id(self, reference: str | Path) -> str | None:
        value = str(reference); return value.removeprefix("resource://") if value.startswith("resource://") else None

    def _load(self, reference: str | Path, kind: str, factory_name: str, cache_key: str | None = None, *args: Any) -> Any:
        key = cache_key or str(reference)
        if key in self._cache: return self._cache[key]
        if self.loader is None: raise RuntimeError(f"No asset loader configured for {kind}")
        resource_id = self.resource_id(reference)
        if resource_id is not None and not self.resources.has(resource_id): raise KeyError(f"Unknown resource: {resource_id}")
        value = getattr(self.loader, factory_name)(self.resolve(reference), *args); self._cache[key] = value; return value

    def load_image(self, reference: str | Path) -> Any: return self._load(reference, "image", "image")
    def load_sound(self, reference: str | Path) -> Any: return self._load(reference, "sound", "sound")
    def load_font(self, reference: str | Path, size: int) -> Any: return self._load(reference, "font", "font", f"{reference}@{int(size)}", int(size))
    def clear(self) -> None: self._cache.clear()
    def inspect(self) -> dict[str, Any]: return {"cached": len(self._cache), "resources": self.resources.inspect()}
