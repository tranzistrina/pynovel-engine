"""Optional extension APIs for project-specific gameplay systems."""

from .commands import CommandContext, CommandRegistry
from .events import Event, EventBus, EventSubscription
from .notifications import Notification, NotificationLog
from .scheduler import GameScheduler, ScheduledEvent
from .scenes import Scene, SceneEntry, SceneStack
from .state import StateNamespace, StateRegistry
from .system import GameSystem, SystemEvent, SystemRegistry

__all__ = [
    "CommandContext", "CommandRegistry",
    "Event", "EventBus", "EventSubscription",
    "Notification", "NotificationLog",
    "GameScheduler", "ScheduledEvent",
    "Scene", "SceneEntry", "SceneStack",
    "StateNamespace", "StateRegistry",
    "GameSystem", "SystemEvent", "SystemRegistry",
]
