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
        binding = InputBinding(str(action), str(event_type), code, int(modifiers))
        self.bindings.append(binding)
        return binding

    def unbind(self, action: str, event_type: str | None = None, code: int | str | None = None, modifiers: int | None = None) -> None:
        self.bindings = [item for item in self.bindings if not (
            item.action == action
            and (event_type is None or item.event_type == str(event_type))
            and (code is None or item.code == code)
            and (modifiers is None or item.modifiers == int(modifiers))
        )]

    def actions_for(self, event_type: str | int, code: int | str, modifiers: int = 0) -> tuple[str, ...]:
        normalized_type = str(event_type)
        normalized_modifiers = int(modifiers)
        return tuple(item.action for item in self.bindings if (
            item.event_type == normalized_type
            and str(item.code) == str(code)
            and item.modifiers == normalized_modifiers
        ))

    def serialize(self) -> list[dict[str, Any]]:
        return [{"action": item.action, "event_type": item.event_type, "code": item.code, "modifiers": item.modifiers} for item in self.bindings]

    @classmethod
    def deserialize(cls, payload: list[dict[str, Any]]) -> "InputMap":
        if not isinstance(payload, list): raise ValueError("Input map payload must be a list")
        return cls([InputBinding(str(item["action"]), str(item["event_type"]), item["code"], int(item.get("modifiers", 0))) for item in payload])
