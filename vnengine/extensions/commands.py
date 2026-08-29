from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True, slots=True)
class CommandContext:
    runtime: Any
    action: Any


CommandHandler = Callable[[CommandContext], None]


class CommandRegistry:
    """Project-extensible command registry for VN actions."""

    def __init__(self) -> None:
        self._handlers: dict[str, CommandHandler] = {}

    def register(self, name: str, handler: CommandHandler) -> None:
        key = str(name).strip()
        if not key:
            raise ValueError("command name must not be empty")
        if key in self._handlers:
            raise ValueError(f"command already registered: {key}")
        self._handlers[key] = handler

    def unregister(self, name: str) -> None:
        self._handlers.pop(name, None)

    def get(self, name: str) -> CommandHandler | None:
        return self._handlers.get(name)

    def names(self) -> tuple[str, ...]:
        return tuple(sorted(self._handlers))

    def dispatch(self, name: str, runtime: Any, action: Any) -> bool:
        handler = self._handlers.get(name)
        if handler is None:
            return False
        handler(CommandContext(runtime, action))
        return True
