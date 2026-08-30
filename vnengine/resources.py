from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True, slots=True)
class Resource:
    id: str
    type: str
    path: str
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {"id": self.id, "type": self.type, "path": self.path, "metadata": dict(self.metadata)}


class ResourceRegistry:
    """Deterministic project resource catalog with lazy loading and caching."""
    def __init__(self, root: str | Path):
        self.root = Path(root).resolve()
        self._resources: dict[str, Resource] = {}
        self._cache: dict[str, Any] = {}

    def register(self, resource_id: str, path: str | Path, resource_type: str, *, metadata: dict[str, Any] | None = None, replace: bool = False) -> Resource:
        key = str(resource_id)
        if key in self._resources and not replace: raise ValueError(f"Resource already registered: {key}")
        resource = Resource(key, str(resource_type), str(path), dict(metadata or {})); self._resources[key] = resource; self._cache.pop(key, None); return resource

    def unregister(self, resource_id: str) -> None:
        self._resources.pop(resource_id, None); self._cache.pop(resource_id, None)

    def has(self, resource_id: str) -> bool: return resource_id in self._resources
    def get(self, resource_id: str) -> Resource:
        try: return self._resources[resource_id]
        except KeyError as exc: raise KeyError(f"Unknown resource: {resource_id}") from exc
    def ids(self) -> tuple[str, ...]: return tuple(self._resources)
    def path(self, resource_id: str) -> Path: return (self.root / self.get(resource_id).path).resolve()
    def exists(self, resource_id: str) -> bool: return self.path(resource_id).is_file()

    def load_text(self, resource_id: str, *, encoding: str = "utf-8") -> str:
        resource = self.get(resource_id)
        if resource.type not in {"text", "script", "json", "shader"}: raise TypeError(f"Resource {resource_id} is not text-like")
        return self.path(resource_id).read_text(encoding=encoding)

    def load_json(self, resource_id: str, *, encoding: str = "utf-8") -> Any:
        import json
        if resource_id not in self._cache: self._cache[resource_id] = json.loads(self.path(resource_id).read_text(encoding=encoding))
        return self._cache[resource_id]

    def inspect(self) -> dict[str, Any]:
        return {"root": str(self.root), "count": len(self._resources), "resources": [{**r.to_dict(), "exists": self.exists(r.id)} for r in self._resources.values()]}

    def clear_cache(self) -> None: self._cache.clear()
