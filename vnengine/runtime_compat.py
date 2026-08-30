from __future__ import annotations

from typing import Any

from .performance import FixedTimestep, Profiler
from .replay import ReplayPlayer, ReplaySession
from .runtime_protocol import RuntimeProtocol, require_runtime


class RuntimeFacade:
    """Uniform high-level facade for runtime, AI agents and deterministic tests."""

    def __init__(
        self,
        runtime: Any,
        *,
        fixed_timestep: float | None = None,
        max_steps: int = 8,
        profiling: bool = False,
    ) -> None:
        self.runtime: RuntimeProtocol = require_runtime(runtime)
        self.replay = ReplaySession()
        self.profiler = Profiler(profiling)
        self.clock = FixedTimestep(fixed_timestep, max_steps) if fixed_timestep is not None else None

    @property
    def running(self) -> bool:
        return bool(self.runtime.running)

    def start(self, **kwargs: Any) -> None:
        self.runtime.start(**kwargs)
        if self.clock is not None:
            self.clock.reset()

    def step(
        self,
        dt: float,
        *,
        events: list[Any] | tuple[Any, ...] = (),
        target: Any = None,
        record: bool = True,
    ) -> dict[str, Any]:
        if record:
            self.replay.record(dt, events)
        handled = 0
        if self.clock is None:
            self._step_once(float(dt), events, target)
            handled = self._last_handled
        else:
            steps = self.clock.advance(float(dt))
            for _ in range(steps):
                self._step_once(self.clock.step, events, target)
                handled += self._last_handled
        return {
            "handled_events": handled,
            "running": bool(self.runtime.running),
            "state": self.runtime.save_state(),
            "profile": self.profiler.snapshot(),
        }

    def _step_once(self, dt: float, events: list[Any] | tuple[Any, ...], target: Any) -> None:
        handled = 0
        with self.profiler.measure("input"):
            for event in events:
                if self.runtime.handle_input(event):
                    handled += 1
        self._last_handled = handled
        with self.profiler.measure("update"):
            self.runtime.update(max(0.0, dt))
        with self.profiler.measure("render"):
            self.runtime.render(target)

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
            "profiling": True,
            "fixed_timestep": self.clock is not None,
        }


__all__ = ["RuntimeFacade"]
