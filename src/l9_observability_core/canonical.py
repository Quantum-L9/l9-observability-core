"""Canonical JSON and digest helpers with no I/O side effects."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel

from .errors import CanonicalizationError
from .primitives import MAX_JSON_SAFE_INTEGER, MIN_JSON_SAFE_INTEGER


def _normalize(value: Any) -> Any:
    if isinstance(value, BaseModel):
        return _normalize(value.model_dump(mode="python", by_alias=True))
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, datetime):
        if value.tzinfo is None or value.utcoffset() is None:
            raise CanonicalizationError("datetime must be timezone-aware")
        utc = value.astimezone(UTC)
        rendered = utc.isoformat(timespec="microseconds")
        return rendered.replace("+00:00", "Z")
    if isinstance(value, Mapping):
        normalized: dict[str, Any] = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise CanonicalizationError("canonical object keys must be strings")
            normalized[key] = _normalize(item)
        return normalized
    if isinstance(value, (list, tuple)):
        return [_normalize(item) for item in value]
    if value is None or isinstance(value, (str, bool)):
        return value
    if isinstance(value, int) and not isinstance(value, bool):
        if not MIN_JSON_SAFE_INTEGER <= value <= MAX_JSON_SAFE_INTEGER:
            raise CanonicalizationError("integer exceeds the JSON safe-integer range")
        return value
    if isinstance(value, float):
        raise CanonicalizationError("floating-point values are forbidden in canonical payloads")
    raise CanonicalizationError(f"unsupported canonical value: {type(value).__name__}")


def canonical_dict(value: Any) -> dict[str, Any]:
    normalized = _normalize(value)
    if not isinstance(normalized, dict):
        raise CanonicalizationError("canonical root must be an object")
    return normalized


def canonical_json(value: Any) -> str:
    try:
        return json.dumps(
            _normalize(value),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise CanonicalizationError(str(exc)) from exc


def canonical_bytes(value: Any) -> bytes:
    try:
        return canonical_json(value).encode("utf-8")
    except UnicodeEncodeError as exc:
        raise CanonicalizationError("canonical JSON must be valid UTF-8") from exc


def sha256_digest(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_bytes(value)).hexdigest()
