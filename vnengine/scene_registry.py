from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class SceneContext:
    scene_id: str
    runtime: Any


SceneFactory = Callable[[SceneContext], Any]


class SceneRegistry:
    """Registry for project-defined runtime scene factories."""
    def __init__(self) -> None:
        self._factories: dict[str, SceneFactory] = {}

    def register(self, scene_id: str, factory: SceneFactory, *, replace: bool = False) -> None:
        if scene_id in self._factories and not replace:
            raise ValueError(f"Scene already registered: {scene_id}")
        self._factories[scene_id] = factory

    def unregister(self, scene_id: str) -> None:
        self._factories.pop(scene_id, None)

    def has(self, scene_id: str) -> bool:
        return scene_id in self._factories

    def create(self, scene_id: str, runtime: Any) -> Any:
        try:
            factory = self._factories[scene_id]
        except KeyError as exc:
            raise KeyError(f"Unknown scene: {scene_id}") from exc
        return factory(SceneContext(scene_id, runtime))

    def ids(self) -> tuple[str, ...]:
        return tuple(self._factories)
