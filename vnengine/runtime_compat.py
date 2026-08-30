from __future__ import annotations

from typing import Any

from .replay import ReplayPlayer, ReplaySession
from .runtime_protocol import RuntimeProtocol, require_runtime


class RuntimeFacade:
    """Uniform high-level facade for runtime, AI agents and deterministic tests."""

    def __init__(self, runtime: Any) -> None:
        self.runtime: RuntimeProtocol = require_runtime(runtime)
        self.replay = ReplaySession()

    @property
    def running(self) -> bool:
        return bool(self.runtime.running)

    def start(self, **kwargs: Any) -> None:
        self.runtime.start(**kwargs)

    def step(self, dt: float, *, events: list[Any] | tuple[Any, ...] = (), target: Any = None, record: bool = True) -> dict[str, Any]:
        if record:
            self.replay.record(dt, events)
        handled = 0
        for event in events:
            if self.runtime.handle_input(event):
                handled += 1
        self.runtime.update(float(dt))
        self.runtime.render(target)
        return {"handled_events": handled, "running": bool(self.runtime.running), "state": self.runtime.save_state()}

    def play_replay(self, replay: ReplaySession | None = None, *, target: Any = None) -> list[dict[str, Any]]:
        player = ReplayPlayer(replay or self.replay)
        results: list[dict[str, Any]] = []
        for frame in iter(player.next_frame, None):
            results.append(self.step(frame.dt, events=frame.events, target=target, record=False))
            if not self.running:
                break
        return results

    def snapshot(self) -> dict[str, Any]:
        return self.runtime.save_state()

    def restore(self, state: dict[str, Any]) -> None:
        self.runtime.load_state(state)

    def stop(self) -> None:
        self.runtime.stop()

    def reset_replay(self) -> None:
        self.replay.clear()

    def capabilities(self) -> dict[str, bool]:
        runtime = self.runtime
        return {
            "input": callable(getattr(runtime, "handle_input", None)),
            "render": callable(getattr(runtime, "render", None)),
            "state": callable(getattr(runtime, "save_state", None)) and callable(getattr(runtime, "load_state", None)),
            "start_stop": callable(getattr(runtime, "start", None)) and callable(getattr(runtime, "stop", None)),
            "replay": True,
        }


__all__ = ["RuntimeFacade"]
