from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Callable
import json
import hashlib


@dataclass(frozen=True, slots=True)
class SaveEnvelope:
    schema_version: int
    engine_version: str
    project_version: str
    metadata: dict[str, Any]
    state: dict[str, Any]
    checksum: str


Migration = Callable[[dict[str, Any]], dict[str, Any]]


class SaveSchema:
    """Versioned save envelope with migrations and optional integrity checksum."""

    def __init__(self, engine_version: str, project_version: str, schema_version: int = 1):
        self.engine_version = engine_version
        self.project_version = project_version
        self.schema_version = int(schema_version)
        self._migrations: dict[tuple[int, int], Migration] = {}

    def add_migration(self, source: int, target: int, migrate: Migration) -> None:
        if target <= source:
            raise ValueError("Migration target must be greater than source")
        self._migrations[(source, target)] = migrate

    def encode(self, state: dict[str, Any], metadata: dict[str, Any] | None = None) -> dict[str, Any]:
        payload = {
            "schema_version": self.schema_version,
            "engine_version": self.engine_version,
            "project_version": self.project_version,
            "metadata": dict(metadata or {}),
            "state": state,
        }
        payload["checksum"] = self._checksum(payload)
        return payload

    def decode(self, payload: dict[str, Any]) -> SaveEnvelope:
        self.validate(payload)
        data = dict(payload.get("state", {}))
        source = int(payload["schema_version"])
        while source != self.schema_version:
            candidates = [(to, fn) for (frm, to), fn in self._migrations.items() if frm == source]
            if not candidates:
                raise ValueError(f"No migration path from save schema {source} to {self.schema_version}")
            target, migrate = min(candidates, key=lambda item: item[0])
            data = migrate(data)
            source = target
        return SaveEnvelope(
            source,
            str(payload.get("engine_version", "unknown")),
            str(payload.get("project_version", "unknown")),
            dict(payload.get("metadata", {})),
            data,
            str(payload["checksum"]),
        )

    def validate(self, payload: dict[str, Any]) -> None:
        required = {"schema_version", "engine_version", "project_version", "metadata", "state", "checksum"}
        missing = required.difference(payload)
        if missing:
            raise ValueError(f"Invalid save: missing {sorted(missing)}")
        if self._checksum({k: payload[k] for k in payload if k != "checksum"}) != payload["checksum"]:
            raise ValueError("Invalid save checksum")
        if int(payload["schema_version"]) > self.schema_version:
            raise ValueError("Save schema is newer than this engine")

    @staticmethod
    def _checksum(payload: dict[str, Any]) -> str:
        raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(raw).hexdigest()
