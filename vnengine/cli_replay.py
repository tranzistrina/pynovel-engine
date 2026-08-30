from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

from .replay import ReplaySession
from .replay_verifier import ReplayVerifier


def load_replay(path: str | Path) -> ReplaySession:
    file = Path(path)
    with file.open("r", encoding="utf-8") as handle:
        return ReplaySession.from_dict(json.load(handle))


def save_replay(path: str | Path, session: ReplaySession) -> None:
    file = Path(path)
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_text(json.dumps(session.to_dict(), ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def verify_replay(path: str | Path, runtime_factory: Callable[[], Any], expected_snapshots: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    result = ReplayVerifier(runtime_factory).run(load_replay(path), expected_snapshots=expected_snapshots)
    return result.to_dict()


__all__ = ["load_replay", "save_replay", "verify_replay"]
