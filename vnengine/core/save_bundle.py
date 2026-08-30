from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Callable


class SaveBundle:
    """Versioned, checksummed container for complete runtime state."""

    FORMAT = 1

    def __init__(self, engine_version: str, project_version: str = "1") -> None:
        self.engine_version = str(engine_version)
        self.project_version = str(project_version)
        self.state: dict[str, Any] = {}
        self.extensions: dict[str, Any] = {}
        self.rng: dict[str, Any] = {}
        self.metadata: dict[str, Any] = {}

    def payload(self) -> dict[str, Any]:
        return {
            "format": self.FORMAT,
            "engine_version": self.engine_version,
            "project_version": self.project_version,
            "state": deepcopy(self.state),
            "extensions": deepcopy(self.extensions),
            "rng": deepcopy(self.rng),
            "metadata": deepcopy(self.metadata),
        }

    @staticmethod
    def _canonical(payload: dict[str, Any]) -> str:
        return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)

    @classmethod
    def _checksum(cls, payload: dict[str, Any]) -> str:
        return hashlib.sha256(cls._canonical(payload).encode("utf-8")).hexdigest()

    def build(self) -> dict[str, Any]:
        payload = self.payload()
        payload["checksum"] = self._checksum(payload)
        return payload

    def save(self, path: str | Path) -> None:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(self.build(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    @classmethod
    def load(cls, path: str | Path, migrations: dict[int, Callable[[dict[str, Any]], dict[str, Any]]] | None = None) -> "SaveBundle":
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
        if not isinstance(raw, dict): raise ValueError("save root must be an object")
        expected = raw.get("checksum")
        payload = {key: value for key, value in raw.items() if key != "checksum"}
        if expected != cls._checksum(payload): raise ValueError("save checksum mismatch")
        version = int(payload.get("format", 0))
        for target in sorted((migrations or {})):
            if version < target:
                payload = migrations[target](deepcopy(payload)); version = target
        if version != cls.FORMAT: raise ValueError(f"unsupported save format: {version}")
        bundle = cls(str(payload.get("engine_version", "unknown")), str(payload.get("project_version", "1")))
        bundle.state = dict(payload.get("state", {})); bundle.extensions = dict(payload.get("extensions", {})); bundle.rng = dict(payload.get("rng", {})); bundle.metadata = dict(payload.get("metadata", {}))
        return bundle
