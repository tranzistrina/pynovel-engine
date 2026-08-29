from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Any


@dataclass(frozen=True, slots=True)
class MovementPolicy:
    """Rules for whether an edge may be traversed and at what cost/speed."""
    allowed: Callable[[str, str], bool] | None = None
    cost_multiplier: Callable[[str, str], float] | None = None
    speed_multiplier: Callable[[str, str], float] | None = None

    def can_traverse(self, source: str, target: str) -> bool:
        return self.allowed(source, target) if self.allowed else True

    def cost(self, source: str, target: str, base: float) -> float:
        value = self.cost_multiplier(source, target) if self.cost_multiplier else 1.0
        if value < 0: raise ValueError("cost multiplier cannot be negative")
        return base * value

    def speed(self, source: str, target: str, base: float) -> float:
        value = self.speed_multiplier(source, target) if self.speed_multiplier else 1.0
        if value <= 0: raise ValueError("speed multiplier must be positive")
        return base * value


class TerrainPolicy:
    """Convenience policy driven by node terrain metadata."""
    def __init__(self, terrain_cost: dict[str, float] | None = None, blocked: set[str] | None = None):
        self.terrain_cost = terrain_cost or {}
        self.blocked = blocked or set()

    def allowed(self, source_node: Any, target_node: Any) -> bool:
        return getattr(target_node, "terrain", "plain") not in self.blocked

    def multiplier(self, source_node: Any, target_node: Any) -> float:
        return float(self.terrain_cost.get(getattr(target_node, "terrain", "plain"), 1.0))
