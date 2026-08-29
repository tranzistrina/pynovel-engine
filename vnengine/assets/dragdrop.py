from __future__ import annotations

MIME_TYPE = "application/x-pynovel-asset"
PREFIX = "pynovel-asset:"


def encode_asset_path(path: str) -> str:
    return f"{PREFIX}{path.replace(chr(92), '/') }"


def decode_asset_path(payload: str) -> str | None:
    if not payload.startswith(PREFIX):
        return None
    path = payload[len(PREFIX):].strip()
    return path or None
