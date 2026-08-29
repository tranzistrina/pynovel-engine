from __future__ import annotations
import json
from pathlib import Path
from typing import Any
from .model import MapDefinition
from .playable import PlayableMap


def load_map_definition(path: str | Path) -> MapDefinition:
    with Path(path).open("r", encoding="utf-8") as handle:
        return MapDefinition.from_dict(json.load(handle))


def load_playable_map(path: str | Path, *, emit=None, hit_radius: float = 24.0) -> PlayableMap:
    with Path(path).open("r", encoding="utf-8") as handle:
        payload: dict[str, Any] = json.load(handle)
    game_map = PlayableMap(MapDefinition.from_dict(payload), emit=emit, hit_radius=hit_radius)
    for entity in payload.get("entities", []):
        game_map.add_entity(entity["id"], entity["node_id"], components=entity.get("components"), metadata=entity.get("metadata"))
    return game_map
