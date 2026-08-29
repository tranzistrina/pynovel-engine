from __future__ import annotations
from dataclasses import dataclass
from typing import Any
import copy
import json


@dataclass(slots=True)
class StateNamespace:
    name: str
    data: dict[str, Any]
    version: int = 1


class StateRegistry:
    """Structured, namespaced game state with deterministic serialization."""

    def __init__(self) -> None:
        self._spaces: dict[str, StateNamespace] = {}
        self._dirty: set[str] = set()

    def register(self, name: str, initial: dict[str, Any] | None = None, version: int = 1) -> None:
        if not name or "." in name:
            raise ValueError("Namespace name must be a non-empty top-level name")
        if name in self._spaces:
            raise ValueError(f"State namespace already registered: {name}")
        self._spaces[name] = StateNamespace(name, copy.deepcopy(initial or {}), int(version))
        self._dirty.add(name)

    def ensure(self, name: str) -> StateNamespace:
        space = self._spaces.get(name)
        if space is None:
            self.register(name)
            space = self._spaces[name]
        return space

    def get(self, path: str, default: Any = None) -> Any:
        parts = self._split(path)
        value: Any = self._spaces.get(parts[0], StateNamespace(parts[0], {})).data
        for key in parts[1:]:
            if not isinstance(value, dict) or key not in value:
                return default
            value = value[key]
        return value

    def set(self, path: str, value: Any) -> None:
        parts = self._split(path)
        space = self.ensure(parts[0])
        if len(parts) == 1:
            if not isinstance(value, dict):
                raise TypeError("Top-level namespace value must be a dict")
            space.data = copy.deepcopy(value)
        else:
            cursor = space.data
            for key in parts[1:-1]:
                child = cursor.get(key)
                if not isinstance(child, dict):
                    child = {}
                    cursor[key] = child
                cursor = child
            cursor[parts[-1]] = copy.deepcopy(value)
        self._dirty.add(parts[0])

    def update(self, namespace: str, values: dict[str, Any]) -> None:
        space = self.ensure(namespace)
        space.data.update(copy.deepcopy(values))
        self._dirty.add(namespace)

    def mark_clean(self) -> None:
        self._dirty.clear()

    def dirty_namespaces(self) -> tuple[str, ...]:
        return tuple(sorted(self._dirty))

    def namespaces(self) -> tuple[str, ...]:
        return tuple(sorted(self._spaces))

    def serialize(self) -> dict[str, Any]:
        return {
            name: {"version": space.version, "data": copy.deepcopy(space.data)}
            for name, space in sorted(self._spaces.items())
        }

    def deserialize(self, payload: dict[str, Any]) -> None:
        for name, raw in sorted(payload.items()):
            data = raw.get("data", {}) if isinstance(raw, dict) else {}
            version = int(raw.get("version", 1)) if isinstance(raw, dict) else 1
            self._spaces[name] = StateNamespace(name, copy.deepcopy(data), version)
        self._dirty.clear()

    def canonical_json(self) -> str:
        return json.dumps(self.serialize(), ensure_ascii=False, sort_keys=True, separators=(",", ":"))

    @staticmethod
    def _split(path: str) -> list[str]:
        parts = [part for part in path.split(".") if part]
        if not parts:
            raise ValueError("State path must not be empty")
        return parts
