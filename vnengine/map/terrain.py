from __future__ import annotations
from dataclasses import dataclass
from typing import Mapping
from .model import MapDefinition, MapConnection


@dataclass(frozen=True, slots=True)
class TerrainRules:
    costs: Mapping[str, float]
    blocked: frozenset[str] = frozenset()

    def multiplier(self, terrain: str) -> float:
        value = float(self.costs.get(terrain, 1.0))
        if value < 0: raise ValueError("terrain cost cannot be negative")
        return value

    def is_blocked(self, terrain: str) -> bool:
        return terrain in self.blocked


def terrain_for(definition: MapDefinition, node_id: str) -> str:
    return definition.node(node_id).terrain


def connection_terrain(definition: MapDefinition, edge: MapConnection) -> str:
    return edge.terrain or terrain_for(definition, edge.target)
