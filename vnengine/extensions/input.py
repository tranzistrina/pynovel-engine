from __future__ import annotations
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class InputBinding:
    action: str
    event_type: str
    code: int | str
    modifiers: int = 0


class InputMap:
    """Logical input actions decoupled from concrete keyboard/mouse events."""

    def __init__(self, bindings: list[InputBinding] | None = None) -> None:
        self.bindings: list[InputBinding] = list(bindings or [])

    def bind(self, action: str, event_type: str, code: int | str, modifiers: int = 0) -> InputBinding:
        binding = InputBinding(action, event_type, code, modifiers)
        self.bindings.append(binding)
        return binding

    def unbind(self, action: str, event_type: str | None = None, code: int | str | None = None) -> None:
        self.bindings = [
            item for item in self.bindings
            if not (item.action == action and (event_type is None or item.event_type == event_type) and (code is None or item.code == code))
        ]

    def actions_for(self, event_type: str, code: int | str, modifiers: int = 0) -> tuple[str, ...]:
        return tuple(
            item.action for item in self.bindings
            if item.event_type == event_type and item.code == code and item.modifiers == modifiers
        )

    def serialize(self) -> list[dict[str, Any]]:
        return [
            {"action": item.action, "event_type": item.event_type, "code": item.code, "modifiers": item.modifiers}
            for item in self.bindings
        ]

    @classmethod
    def deserialize(cls, payload: list[dict[str, Any]]) -> "InputMap":
        return cls([
            InputBinding(str(item["action"]), str(item["event_type"]), item["code"], int(item.get("modifiers", 0)))
            for item in payload
        ])
