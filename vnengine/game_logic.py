from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class Condition:
    variable: str
    operator: str
    value: Any

    def evaluate(self, state: dict[str, Any]) -> bool:
        left = state.get(self.variable)
        right = self.value
        ops = {
            "==": lambda: left == right,
            "!=": lambda: left != right,
            ">": lambda: left is not None and left > right,
            ">=": lambda: left is not None and left >= right,
            "<": lambda: left is not None and left < right,
            "<=": lambda: left is not None and left <= right,
            "in": lambda: left in right,
            "not_in": lambda: left not in right,
        }
        try:
            return bool(ops[self.operator]())
        except (KeyError, TypeError):
            return False


class GameLogic:
    """Deterministic state and action executor for declarative games."""

    def __init__(self, state: dict[str, Any] | None = None):
        self.state: dict[str, Any] = dict(state or {})
        self.events: list[dict[str, Any]] = []

    def get(self, key: str, default: Any = None) -> Any:
        return self.state.get(key, default)

    def set(self, key: str, value: Any) -> Any:
        self.state[key] = value
        self.events.append({"type": "set", "key": key, "value": value})
        return value

    def change(self, key: str, amount: float) -> Any:
        current = self.state.get(key, 0)
        value = current + amount
        self.state[key] = value
        self.events.append({"type": "change", "key": key, "amount": amount, "value": value})
        return value

    def check(self, condition: dict[str, Any] | Condition) -> bool:
        if isinstance(condition, dict):
            condition = Condition(str(condition.get("variable", "")), str(condition.get("operator", "==")), condition.get("value"))
        return condition.evaluate(self.state)

    def execute(self, action: dict[str, Any]) -> dict[str, Any]:
        kind = action.get("type")
        if kind == "set":
            self.set(str(action["variable"]), action.get("value"))
            return {"type": "set", "variable": action["variable"]}
        if kind == "change":
            self.change(str(action["variable"]), action.get("amount", 1))
            return {"type": "change", "variable": action["variable"]}
        if kind == "emit":
            event = {"type": "event", "name": str(action.get("name", "")), "data": dict(action.get("data", {}))}
            self.events.append(event)
            return event
        if kind == "if":
            branch = action.get("then", []) if self.check(action.get("condition", {})) else action.get("else", [])
            for nested in branch:
                self.execute(nested)
            return {"type": "if", "matched": self.check(action.get("condition", {}))}
        raise ValueError(f"Unsupported logic action: {kind}")

    def serialize(self) -> dict[str, Any]:
        return {"variables": dict(self.state)}

    def deserialize(self, payload: dict[str, Any]) -> None:
        self.state = dict(payload.get("variables", {}))
        self.events.clear()
