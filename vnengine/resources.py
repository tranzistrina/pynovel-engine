from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass
from pathlib import Path
from typing import Any
import json


@dataclass(frozen=True, slots=True)
class Resource:
    id: str
    type: str
    path: str
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {"id": self.id, "type": self.type, "path": self.path, "metadata": dict(self.metadata)}


class ResourceRegistry:
    """Deterministic project resource catalog with safe paths and bounded data caching."""

    def __init__(self, root: str | Path, *, max_cache: int = 256):
        if int(max_cache) < 0:
            raise ValueError("max_cache must be non-negative")
        self.root = Path(root).resolve()
        self.max_cache = int(max_cache)
        self._resources: dict[str, Resource] = {}
        self._cache: OrderedDict[str, Any] = OrderedDict()
        self._cache_hits = 0
        self._cache_misses = 0
        self._evictions = 0

    def register(self, resource_id: str, path: str | Path, resource_type: str, *, metadata: dict[str, Any] | None = None, replace: bool = False) -> Resource:
        key = str(resource_id)
        if key in self._resources and not replace:
            raise ValueError(f"Resource already registered: {key}")
        self._safe_path(path)
        resource = Resource(key, str(resource_type), str(path).replace("\\", "/"), dict(metadata or {}))
        self._resources[key] = resource
        self.evict(key)
        return resource

    def unregister(self, resource_id: str) -> None:
        self._resources.pop(resource_id, None)
        self.evict(resource_id)

    def has(self, resource_id: str) -> bool:
        return resource_id in self._resources

    def get(self, resource_id: str) -> Resource:
        try:
            return self._resources[resource_id]
        except KeyError as exc:
            raise KeyError(f"Unknown resource: {resource_id}") from exc

    def ids(self) -> tuple[str, ...]:
        return tuple(sorted(self._resources))

    def path(self, resource_id: str) -> Path:
        return self._safe_path(self.get(resource_id).path)

    def exists(self, resource_id: str) -> bool:
        return self.path(resource_id).is_file()

    def load_text(self, resource_id: str, *, encoding: str = "utf-8") -> str:
        resource = self.get(resource_id)
        if resource.type not in {"text", "script", "json", "shader"}:
            raise TypeError(f"Resource {resource_id} is not text-like")
        key = f"text:{resource_id}:{encoding}"
        cached = self._cached(key)
        if cached is not None:
            return cached
        value = self.path(resource_id).read_text(encoding=encoding)
        self._store(key, value)
        return value

    def load_json(self, resource_id: str, *, encoding: str = "utf-8") -> Any:
        key = f"json:{resource_id}:{encoding}"
        cached = self._cached(key)
        if cached is not None:
            return cached
        value = json.loads(self.path(resource_id).read_text(encoding=encoding))
        self._store(key, value)
        return value

    def evict(self, resource_id: str) -> bool:
        keys = [key for key in self._cache if key.split(":", 2)[1] == resource_id]
        removed = False
        for key in keys:
            self._cache.pop(key, None)
            removed = True
        return removed

    def clear_cache(self) -> None:
        self._cache.clear()

    def cache_stats(self) -> dict[str, Any]:
        total = self._cache_hits + self._cache_misses
        return {
            "cached": len(self._cache),
            "max_cache": self.max_cache,
            "hits": self._cache_hits,
            "misses": self._cache_misses,
            "evictions": self._evictions,
            "hit_rate": self._cache_hits / total if total else 0.0,
        }

    def inspect(self) -> dict[str, Any]:
        return {
            "root": str(self.root),
            "count": len(self._resources),
            "resources": [{**r.to_dict(), "exists": self.exists(r.id)} for r in self._resources.values()],
            "cache": self.cache_stats(),
        }

    def _cached(self, key: str) -> Any:
        if key not in self._cache:
            self._cache_misses += 1
            return None
        self._cache_hits += 1
        value = self._cache.pop(key)
        self._cache[key] = value
        return value

    def _store(self, key: str, value: Any) -> None:
        if self.max_cache <= 0:
            return
        if key in self._cache:
            self._cache.pop(key)
        elif len(self._cache) >= self.max_cache:
            self._cache.popitem(last=False)
            self._evictions += 1
        self._cache[key] = value

    def _safe_path(self, path: str | Path) -> Path:
        candidate = (self.root / Path(path)).resolve()
        try:
            candidate.relative_to(self.root)
        except ValueError as exc:
            raise ValueError(f"Resource path escapes project root: {path}") from exc
        return candidate
