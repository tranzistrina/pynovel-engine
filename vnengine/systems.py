from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass(frozen=True, slots=True)
class SystemSpec:
    name: str
    kind: str = "generic"
    requires: tuple[str, ...] = ()
    before: tuple[str, ...] = ()
    after: tuple[str, ...] = ()
    enabled: bool = True
    priority: int = 0
    settings: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "requires": list(self.requires),
            "before": list(self.before),
            "after": list(self.after),
            "enabled": self.enabled,
            "priority": self.priority,
            "settings": dict(self.settings),
        }


class SystemRegistry:
    """Data-driven system definitions plus optional code factories."""

    def __init__(self) -> None:
        self._specs: dict[str, SystemSpec] = {}
        self._factories: dict[str, Callable[[SystemSpec], Any]] = {}

    def register(self, name: str, *, kind: str = "generic", requires: tuple[str, ...] = (),
                 before: tuple[str, ...] = (), after: tuple[str, ...] = (), enabled: bool = True,
                 priority: int = 0, settings: dict[str, Any] | None = None,
                 factory: Callable[[SystemSpec], Any] | None = None, replace: bool = False) -> SystemSpec:
        key = str(name)
        if not key:
            raise ValueError("System name must not be empty")
        if key in self._specs and not replace:
            raise ValueError(f"System already registered: {key}")
        spec = SystemSpec(key, str(kind), tuple(map(str, requires)), tuple(map(str, before)),
                          tuple(map(str, after)), bool(enabled), int(priority), dict(settings or {}))
        self._specs[key] = spec
        if factory is not None:
            self._factories[key] = factory
        elif key in self._factories:
            self._factories.pop(key)
        return spec

    def register_data(self, definitions: dict[str, Any], *, replace: bool = False) -> list[SystemSpec]:
        if not isinstance(definitions, dict):
            raise ValueError("System definitions must be an object")
        result: list[SystemSpec] = []
        for name, raw in sorted(definitions.items()):
            if not isinstance(raw, dict):
                raise ValueError(f"System definition must be an object: {name}")
            result.append(self.register(
                str(name),
                kind=str(raw.get("kind", "generic")),
                requires=tuple(raw.get("requires", ())),
                before=tuple(raw.get("before", ())),
                after=tuple(raw.get("after", ())),
                enabled=bool(raw.get("enabled", True)),
                priority=int(raw.get("priority", 0)),
                settings=raw.get("settings", {}),
                replace=replace,
            ))
        errors = self.validate_definitions()
        if errors:
            raise ValueError("; ".join(errors))
        return result

    def has(self, name: str) -> bool:
        return str(name) in self._specs

    def get(self, name: str) -> SystemSpec:
        try:
            return self._specs[str(name)]
        except KeyError as exc:
            raise KeyError(f"Unknown system: {name}") from exc

    def names(self) -> tuple[str, ...]:
        return tuple(sorted(self._specs))

    def enabled_specs(self) -> tuple[SystemSpec, ...]:
        return tuple(spec for spec in self._ordered_specs() if spec.enabled)

    def instantiate(self, name: str) -> Any:
        spec = self.get(name)
        factory = self._factories.get(spec.name)
        return factory(spec) if factory is not None else None

    def validate_definitions(self) -> list[str]:
        errors: list[str] = []
        names = set(self._specs)
        for name, spec in sorted(self._specs.items()):
            missing_components = [item for item in spec.requires if not item]
            if missing_components:
                errors.append(f"System {name} has an empty component requirement")
            for target in (*spec.before, *spec.after):
                if target == name:
                    errors.append(f"System {name} cannot order itself")
            for target in spec.before + spec.after:
                if target not in names:
                    errors.append(f"System {name} references unknown system order target: {target}")
        return errors

    def order(self) -> tuple[str, ...]:
        ordered = [spec.name for spec in self._ordered_specs()]
        return tuple(ordered)

    def serialize(self) -> dict[str, Any]:
        return {name: self._specs[name].to_dict() for name in sorted(self._specs)}

    def _ordered_specs(self) -> list[SystemSpec]:
        specs = {name: spec for name, spec in self._specs.items()}
        indegree = {name: 0 for name in specs}
        edges: dict[str, set[str]] = {name: set() for name in specs}
        for spec in specs.values():
            for target in spec.before:
                if target in specs and target not in edges[spec.name]:
                    edges[spec.name].add(target); indegree[target] += 1
            for target in spec.after:
                if target in specs and spec.name not in edges[target]:
                    edges[target].add(spec.name); indegree[spec.name] += 1
        ready = sorted((name for name, count in indegree.items() if count == 0), key=lambda n: (-specs[n].priority, n))
        result: list[str] = []
        while ready:
            current = ready.pop(0)
            result.append(current)
            for target in sorted(edges[current]):
                indegree[target] -= 1
                if indegree[target] == 0:
                    ready.append(target)
                    ready.sort(key=lambda n: (-specs[n].priority, n))
        if len(result) != len(specs):
            raise ValueError("System dependency graph contains a cycle")
        return [specs[name] for name in result]


__all__ = ["SystemSpec", "SystemRegistry"]
