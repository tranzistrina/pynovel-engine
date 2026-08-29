"""Optional extension APIs for project-specific gameplay systems."""

from .events import Event, EventBus, EventSubscription
from .scenes import Scene, SceneEntry, SceneStack
from .state import StateNamespace, StateRegistry
from .system import GameSystem, SystemEvent, SystemRegistry

__all__ = [
    "Event", "EventBus", "EventSubscription",
    "Scene", "SceneEntry", "SceneStack",
    "StateNamespace", "StateRegistry",
    "GameSystem", "SystemEvent", "SystemRegistry",
]
