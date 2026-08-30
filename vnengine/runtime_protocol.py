from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class RuntimeProtocol(Protocol):
    """Stable public lifecycle contract shared by all PyNovel runtimes."""

    running: bool

    def start(self, **kwargs: Any) -> None: ...
    def update(self, dt: float) -> None: ...
    def handle_input(self, event: Any) -> bool: ...
    def render(self, target: Any) -> None: ...
    def save_state(self) -> dict[str, Any]: ...
    def load_state(self, state: dict[str, Any]) -> None: ...
    def stop(self) -> None: ...


def require_runtime(value: Any) -> RuntimeProtocol:
    """Validate the lifecycle surface once at integration boundaries."""
    required = ("start", "update", "handle_input", "render", "save_state", "load_state", "stop")
    missing = [name for name in required if not callable(getattr(value, name, None))]
    if missing:
        raise TypeError(f"Runtime does not satisfy RuntimeProtocol: missing {missing}")
    return value


class CoreRuntimeAdapter:
    """Expose the core story runtime through the project runtime contract."""

    def __init__(self, runtime: Any) -> None:
        self.runtime = runtime

    @property
    def running(self) -> bool:
        return bool(self.runtime.state.running)

    def start(self, **_: Any) -> None:
        self.runtime.new_game()

    def update(self, dt: float) -> None:
        self.runtime.update(float(dt))

    def handle_input(self, event: Any) -> bool:
        handler = getattr(self.runtime, "dispatch_input", None)
        if callable(handler):
            return bool(handler(event))
        return False

    def render(self, target: Any) -> None:
        draw = getattr(self.runtime, "draw", None)
        if callable(draw):
            draw(target)

    def save_state(self) -> dict[str, Any]:
        state = self.runtime.state
        return {
            "index": state.index,
            "variables": dict(state.variables),
            "history": list(state.history),
            "background": state.background_path,
        }

    def load_state(self, state: dict[str, Any]) -> None:
        current = self.runtime.state
        current.index = int(state.get("index", 0))
        current.variables = dict(state.get("variables", {}))
        current.history = [tuple(item) for item in state.get("history", [])]
        current.background_path = state.get("background")

    def stop(self) -> None:
        self.runtime.state.running = False


class ExtensibleRuntimeAdapter(CoreRuntimeAdapter):
    """Compatibility alias for the extensible runtime lifecycle."""


__all__ = ["RuntimeProtocol", "require_runtime", "CoreRuntimeAdapter", "ExtensibleRuntimeAdapter"]
