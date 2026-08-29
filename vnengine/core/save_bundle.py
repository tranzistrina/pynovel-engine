from __future__ import annotations
import hashlib
import json
from pathlib import Path
from typing import Any, Callable


class SaveBundle:
    """Versioned container for engine, project, extension and RNG state."""

    FORMAT = 1

    def __init__(self, engine_version: str, project_version: str = "1") -> None:
        self.engine_version = engine_version
        self.project_version = project_version
        self.state: dict[str, Any] = {}
        self.extensions: dict[str, Any] = {}
        self.rng: dict[str, Any] = {}

    def build(self) -> dict[str, Any]:
        payload = {
            "format": self.FORMAT,
            "engine_version": self.engine_version,
            "project_version": self.project_version,
            "state": self.state,
            "extensions": self.extensions,
            "rng": self.rng,
        }
        canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        payload["checksum"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        return payload

    def save(self, path: str | Path) -> None:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(self.build(), ensure_ascii=False, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: str | Path, migrations: dict[int, Callable[[dict[str, Any]], dict[str, Any]]] | None = None) -> "SaveBundle":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        expected = data.pop("checksum", None)
        canonical = json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        actual = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        if expected != actual:
            raise ValueError("save checksum mismatch")
        version = int(data.get("format", 0))
        for target in sorted((migrations or {})):
            if version < target:
                data = migrations[target](data)
                version = target
        if version != cls.FORMAT:
            raise ValueError(f"unsupported save format: {version}")
        bundle = cls(str(data.get("engine_version", "unknown")), str(data.get("project_version", "1")))
        bundle.state = dict(data.get("state", {}))
        bundle.extensions = dict(data.get("extensions", {}))
        bundle.rng = dict(data.get("rng", {}))
        return bundle
