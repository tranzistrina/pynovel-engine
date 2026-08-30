from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from .replay import ReplayPlayer, ReplaySession


@dataclass(frozen=True, slots=True)
class ReplayDifference:
    frame: int
    path: str
    expected: Any
    actual: Any

    def to_dict(self) -> dict[str, Any]:
        return {
            "frame": self.frame,
            "path": self.path,
            "expected": self.expected,
            "actual": self.actual,
        }


@dataclass(frozen=True, slots=True)
class ReplayVerification:
    passed: bool
    frames_checked: int
    expected_digest: str
    actual_digest: str
    differences: tuple[ReplayDifference, ...] = ()

    @property
    def first_difference(self) -> ReplayDifference | None:
        return self.differences[0] if self.differences else None

    def to_dict(self) -> dict[str, Any]:
        data = {
            "passed": self.passed,
            "frames_checked": self.frames_checked,
            "expected_digest": self.expected_digest,
            "actual_digest": self.actual_digest,
            "differences": [item.to_dict() for item in self.differences],
        }
        if self.first_difference is not None:
            data["first_difference"] = self.first_difference.to_dict()
        return data


class ReplayVerifier:
    """Run a replay against a runtime and report the first deterministic divergence."""

    def __init__(self, runtime_factory: Callable[[], Any]) -> None:
        self.runtime_factory = runtime_factory

    def run(
        self,
        session: ReplaySession,
        *,
        expected_snapshots: list[dict[str, Any]] | tuple[dict[str, Any], ...] | None = None,
        max_differences: int = 20,
    ) -> ReplayVerification:
        runtime = self.runtime_factory()
        runtime.start()
        player = ReplayPlayer(session)
        actual_snapshots: list[dict[str, Any]] = []
        try:
            while (frame := player.next_frame()) is not None:
                events = list(frame.events)
                for event in events:
                    runtime.handle_input(event)
                runtime.update(frame.dt)
                actual_snapshots.append(runtime.save_state())
        finally:
            runtime.stop()

        expected = list(expected_snapshots or [])
        differences: list[ReplayDifference] = []
        for frame_index, (left, right) in enumerate(zip(expected, actual_snapshots)):
            self._compare(left, right, f"frames[{frame_index}].state", frame_index, differences, max_differences)
            if len(differences) >= max_differences:
                break
        if len(expected) != len(actual_snapshots) and len(differences) < max_differences:
            differences.append(
                ReplayDifference(
                    min(len(expected), len(actual_snapshots)),
                    "frames.length",
                    len(expected),
                    len(actual_snapshots),
                )
            )

        expected_session = ReplaySession(list(session.frames), dict(session.metadata))
        actual_session = ReplaySession(list(session.frames), dict(session.metadata))
        if actual_snapshots:
            actual_session.metadata["final_snapshot"] = actual_snapshots[-1]
        expected_session.metadata["snapshots"] = expected
        actual_session.metadata["snapshots"] = actual_snapshots
        expected_digest = expected_session.digest()
        actual_digest = actual_session.digest()
        return ReplayVerification(
            not differences,
            len(actual_snapshots),
            expected_digest,
            actual_digest,
            tuple(differences),
        )

    @staticmethod
    def _compare(expected: Any, actual: Any, path: str, frame: int, out: list[ReplayDifference], limit: int) -> None:
        if len(out) >= limit:
            return
        if type(expected) is not type(actual):
            out.append(ReplayDifference(frame, path, expected, actual))
            return
        if isinstance(expected, dict):
            keys = sorted(set(expected) | set(actual), key=str)
            for key in keys:
                key_path = f"{path}.{key}"
                if key not in expected or key not in actual:
                    out.append(ReplayDifference(frame, key_path, expected.get(key), actual.get(key)))
                else:
                    ReplayVerifier._compare(expected[key], actual[key], key_path, frame, out, limit)
                    if len(out) >= limit:
                        return
            return
        if isinstance(expected, (list, tuple)):
            if len(expected) != len(actual):
                out.append(ReplayDifference(frame, f"{path}.length", len(expected), len(actual)))
                if len(out) >= limit:
                    return
            for index, (left, right) in enumerate(zip(expected, actual)):
                ReplayVerifier._compare(left, right, f"{path}[{index}]", frame, out, limit)
                if len(out) >= limit:
                    return
            return
        if expected != actual:
            out.append(ReplayDifference(frame, path, expected, actual))


__all__ = ["ReplayDifference", "ReplayVerification", "ReplayVerifier"]
