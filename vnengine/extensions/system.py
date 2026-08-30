from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Protocol


class GameSystem(Protocol):
    name: str
    def update(self, dt: float, state: Any) -> None: ...
    def handle_event(self, event: object, state: Any) -> bool: ...
    def serialize(self) -> dict[str, Any]: ...
    def deserialize(self, data: dict[str, Any]) -> None: ...


@dataclass(frozen=True, slots=True)
class SystemEvent:
    name: str
    data: dict[str, Any]


class SystemRegistry:
    def __init__(self) -> None:
        self._systems: dict[str, GameSystem] = {}

    def register(self, system: GameSystem) -> None:
        if not system.name:
            raise ValueError("GameSystem name must not be empty")
        if system.name in self._systems:
            raise ValueError(f"GameSystem already registered: {system.name}")
        self._systems[system.name] = system

    def unregister(self, name: str) -> None:
        self._systems.pop(name, None)

    def get(self, name: str) -> GameSystem | None:
        return self._systems.get(name)

    def values(self) -> tuple[GameSystem, ...]:
        return tuple(self._systems.values())

    def items(self) -> tuple[tuple[str, GameSystem], ...]:
        return tuple(self._systems.items())

    def names(self) -> tuple[str, ...]:
        return tuple(self._systems)

    def serialize(self) -> dict[str, dict[str, Any]]:
        return {name: system.serialize() for name, system in sorted(self._systems.items()) if hasattr(system, "serialize")}

    def deserialize(self, payload: dict[str, dict[str, Any]]) -> None:
        for name, data in payload.items():
            system = self._systems.get(name)
            if system is not None and hasattr(system, "deserialize"):
                system.deserialize(data)
