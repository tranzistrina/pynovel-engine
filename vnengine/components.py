from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable
import copy


@dataclass(frozen=True, slots=True)
class ComponentSpec:
    name: str
    factory: Callable[..., Any] | None = None
    requires: tuple[str, ...] = ()
    defaults: dict[str, Any] = field(default_factory=dict)

    def create(self, value: Any = None) -> Any:
        payload = copy.deepcopy(self.defaults)
        if value is not None:
            if isinstance(payload, dict) and isinstance(value, dict):
                payload.update(copy.deepcopy(value))
            else:
                payload = copy.deepcopy(value)
        return self.factory(payload) if self.factory is not None else payload


class ComponentRegistry:
    """Typed component definitions and deterministic dependency validation."""

    def __init__(self) -> None:
        self._specs: dict[str, ComponentSpec] = {}

    def register(self, name: str, *, factory: Callable[..., Any] | None = None,
                 requires: tuple[str, ...] = (), defaults: dict[str, Any] | None = None,
                 replace: bool = False) -> ComponentSpec:
        key = str(name)
        if not key:
            raise ValueError("Component name must not be empty")
        if key in self._specs and not replace:
            raise ValueError(f"Component already registered: {key}")
        spec = ComponentSpec(key, factory, tuple(map(str, requires)), copy.deepcopy(defaults or {}))
        self._specs[key] = spec
        return spec

    def has(self, name: str) -> bool:
        return str(name) in self._specs

    def get(self, name: str) -> ComponentSpec:
        try:
            return self._specs[str(name)]
        except KeyError as exc:
            raise KeyError(f"Unknown component type: {name}") from exc

    def names(self) -> tuple[str, ...]:
        return tuple(sorted(self._specs))

    def create(self, name: str, value: Any = None) -> Any:
        return self.get(name).create(value)

    def validate(self, components: dict[str, Any]) -> list[str]:
        errors: list[str] = []
        present = {str(name) for name in components}
        for name in sorted(present):
            if name not in self._specs:
                errors.append(f"Unknown component type: {name}")
                continue
            for requirement in self._specs[name].requires:
                if requirement not in present:
                    errors.append(f"Component {name} requires {requirement}")
        return errors


class ComponentSystem:
    """Small runtime system contract for processing entities with required components."""

    def __init__(self, name: str, *, requires: tuple[str, ...] = ()) -> None:
        self.name = str(name)
        self.requires = tuple(map(str, requires))

    def update(self, dt: float, entities: Any, state: Any) -> None:
        return None

    def process(self, entity: Any, dt: float, state: Any) -> None:
        return None

    def run(self, dt: float, registry: Any, state: Any) -> int:
        processed = 0
        for entity in registry.all():
            if all(entity.has_component(name) for name in self.requires):
                self.process(entity, dt, state)
                processed += 1
        self.update(dt, registry, state)
        return processed


__all__ = ["ComponentSpec", "ComponentRegistry", "ComponentSystem"]
