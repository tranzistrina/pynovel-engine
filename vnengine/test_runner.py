from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable

from .headless import HeadlessHarness


@dataclass(frozen=True, slots=True)
class TestCase:
    name: str
    frames: int = 1
    dt: float = 1.0 / 60.0
    expected_scene: str | None = None
    expected_variables: dict[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class TestResult:
    name: str
    passed: bool
    frames: int
    scene: str | None
    errors: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class HeadlessTestRunner:
    """Small deterministic integration-test runner for game projects."""

    def __init__(self, project: str | Path):
        self.project = str(Path(project).resolve())

    def run_case(self, case: TestCase) -> TestResult:
        harness = HeadlessHarness(self.project)
        errors: list[str] = []
        try:
            harness.start()
            frames = harness.run(case.frames, dt=case.dt)
            snapshot = harness.snapshot()
            if case.expected_scene is not None and snapshot.scene != case.expected_scene:
                errors.append(f"scene: expected {case.expected_scene!r}, got {snapshot.scene!r}")
            if case.expected_variables:
                actual = snapshot.state.get("logic", {}).get("variables", {})
                for key, expected in case.expected_variables.items():
                    if actual.get(key) != expected:
                        errors.append(f"variable {key}: expected {expected!r}, got {actual.get(key)!r}")
            return TestResult(case.name, not errors, len(frames), snapshot.scene, tuple(errors))
        except Exception as exc:
            return TestResult(case.name, False, 0, harness.runtime.scene_id, (f"{type(exc).__name__}: {exc}",))
        finally:
            harness.stop()

    def run(self, cases: list[TestCase]) -> dict[str, Any]:
        results = [self.run_case(case) for case in cases]
        passed = sum(item.passed for item in results)
        return {"passed": passed, "failed": len(results) - passed, "total": len(results), "results": [item.to_dict() for item in results]}

    @staticmethod
    def load_cases(path: str | Path) -> list[TestCase]:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        if isinstance(data, dict): data = data.get("tests", [])
        if not isinstance(data, list): raise ValueError("Test specification must contain a list")
        return [TestCase(str(item["name"]), int(item.get("frames", 1)), float(item.get("dt", 1.0 / 60.0)), item.get("expected_scene"), dict(item.get("expected_variables", {})) or None) for item in data]
