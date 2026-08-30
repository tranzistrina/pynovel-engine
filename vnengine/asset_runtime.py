from __future__ import annotations

from collections import OrderedDict
from pathlib import Path
from typing import Any

from .resources import ResourceRegistry


class AssetRuntime:
    """Frontend-agnostic typed asset facade with bounded lazy caching."""

    def __init__(self, resources: ResourceRegistry, *, loader: Any = None, max_cache: int = 256):
        if int(max_cache) < 0:
            raise ValueError("max_cache must be non-negative")
        self.resources = resources
        self.loader = loader
        self.max_cache = int(max_cache)
        self._cache: OrderedDict[str, Any] = OrderedDict()
        self._hits = 0
        self._misses = 0
        self._evictions = 0

    def resolve(self, reference: str | Path) -> Path:
        value = str(reference)
        return self.resources.path(value.removeprefix("resource://")) if value.startswith("resource://") else self.resources._safe_path(value)

    def resource_id(self, reference: str | Path) -> str | None:
        value = str(reference)
        return value.removeprefix("resource://") if value.startswith("resource://") else None

    def _load(self, reference: str | Path, kind: str, factory_name: str, cache_key: str | None = None, *args: Any) -> Any:
        key = cache_key or str(reference)
        if key in self._cache:
            self._hits += 1
            value = self._cache.pop(key)
            self._cache[key] = value
            return value
        self._misses += 1
        if self.loader is None:
            raise RuntimeError(f"No asset loader configured for {kind}")
        resource_id = self.resource_id(reference)
        if resource_id is not None and not self.resources.has(resource_id):
            raise KeyError(f"Unknown resource: {resource_id}")
        value = getattr(self.loader, factory_name)(self.resolve(reference), *args)
        if self.max_cache > 0:
            if len(self._cache) >= self.max_cache:
                self._cache.popitem(last=False)
                self._evictions += 1
            self._cache[key] = value
        return value

    def load_image(self, reference: str | Path) -> Any:
        return self._load(reference, "image", "image")

    def load_sound(self, reference: str | Path) -> Any:
        return self._load(reference, "sound", "sound")

    def load_font(self, reference: str | Path, size: int) -> Any:
        return self._load(reference, "font", "font", f"{reference}@{int(size)}", int(size))

    def preload(self, references: list[str | Path] | tuple[str | Path, ...], kind: str) -> int:
        method = {"image": self.load_image, "sound": self.load_sound}.get(kind)
        if method is None:
            raise ValueError(f"Unsupported preload kind: {kind}")
        count = 0
        for reference in references:
            method(reference)
            count += 1
        return count

    def evict(self, reference: str | Path) -> bool:
        key = str(reference)
        return self._cache.pop(key, None) is not None

    def clear(self) -> None:
        self._cache.clear()

    def stats(self) -> dict[str, Any]:
        return {
            "cached": len(self._cache),
            "max_cache": self.max_cache,
            "hits": self._hits,
            "misses": self._misses,
            "evictions": self._evictions,
            "hit_rate": self._hits / (self._hits + self._misses) if self._hits + self._misses else 0.0,
        }

    def inspect(self) -> dict[str, Any]:
        return {"cache": self.stats(), "resources": self.resources.inspect()}
