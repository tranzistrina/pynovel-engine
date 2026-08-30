from __future__ import annotations

from typing import Any

from .runtime_protocol import RuntimeProtocol, require_runtime


class RuntimeAdapter:
    """Small façade that normalizes optional runtime capabilities.

    The façade is intentionally boring: AI tools, frontends and test runners
    use this surface instead of branching on concrete runtime implementations.
    """

    def __init__(self, runtime: Any) -> None:
        self.runtime: RuntimeProtocol = require_runtime(runtime)

    @property
    def running(self) -> bool:
        return bool(self.runtime.running)

    def start(self, **kwargs: Any) -> None:
        self.runtime.start(**kwargs)

    def step(self, dt: float = 1.0 / 60.0, event: Any = None) -> None:
        if event is not None:
            self.runtime.handle_input(event)
        self.runtime.update(max(0.0, float(dt)))

    def input(self, event: Any) -> bool:
        return bool(self.runtime.handle_input(event))

    def render(self, target: Any = None) -> None:
        self.runtime.render(target)

    def snapshot(self) -> dict[str, Any]:
        return dict(self.runtime.save_state())

    def restore(self, state: dict[str, Any]) -> None:
        self.runtime.load_state(dict(state))

    def stop(self) -> None:
        self.runtime.stop()

    def capabilities(self) -> dict[str, bool]:
        runtime = self.runtime
        optional = (
            "switch_scene", "push_scene", "pop_scene", "save_bundle",
            "load_bundle", "evaluate", "set", "change", "emit",
        )
        return {name: callable(getattr(runtime, name, None)) for name in optional}


__all__ = ["RuntimeAdapter"]
