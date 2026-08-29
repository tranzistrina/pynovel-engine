from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(slots=True)
class Notification:
    """Serializable presentation record for a project notification."""

    id: str
    title: str
    body: str = ""
    severity: str = "info"
    icon: str | None = None
    timestamp: int = 0
    action: str | None = None
    unread: bool = True

    def serialize(self) -> dict[str, Any]:
        return asdict(self)


class NotificationLog:
    """Ordered, deterministic notification history owned by the runtime."""

    def __init__(self) -> None:
        self._items: list[Notification] = []
        self._next_id = 1

    @property
    def items(self) -> tuple[Notification, ...]:
        return tuple(self._items)

    @property
    def unread_count(self) -> int:
        return sum(item.unread for item in self._items)

    def add(
        self,
        title: str,
        body: str = "",
        *,
        severity: str = "info",
        icon: str | None = None,
        timestamp: int = 0,
        action: str | None = None,
        notification_id: str | None = None,
    ) -> Notification:
        identifier = notification_id or f"notification-{self._next_id}"
        if notification_id is None:
            self._next_id += 1
        item = Notification(identifier, str(title), str(body), str(severity), icon, int(timestamp), action)
        self._items.append(item)
        return item

    def mark_read(self, notification_id: str) -> bool:
        for item in self._items:
            if item.id == notification_id:
                item.unread = False
                return True
        return False

    def mark_all_read(self) -> None:
        for item in self._items:
            item.unread = False

    def remove(self, notification_id: str) -> bool:
        before = len(self._items)
        self._items[:] = [item for item in self._items if item.id != notification_id]
        return len(self._items) != before

    def clear(self) -> None:
        self._items.clear()

    def serialize(self) -> dict[str, Any]:
        return {"next_id": self._next_id, "items": [item.serialize() for item in self._items]}

    def deserialize(self, data: dict[str, Any] | None) -> None:
        payload = data or {}
        self._next_id = max(1, int(payload.get("next_id", 1)))
        self._items = [Notification(**item) for item in payload.get("items", [])]
        existing_numbers = [int(item.id.rsplit("-", 1)[1]) for item in self._items if item.id.startswith("notification-") and item.id.rsplit("-", 1)[-1].isdigit()]
        if existing_numbers:
            self._next_id = max(self._next_id, max(existing_numbers) + 1)
