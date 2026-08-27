"""Bounded immutable scalar attribute validation."""

from __future__ import annotations

import re
from collections.abc import Iterator, Mapping
from types import MappingProxyType
from typing import TypeAlias

from .errors import ObservabilityError
from .primitives import MAX_JSON_SAFE_INTEGER, MIN_JSON_SAFE_INTEGER

AttributeValue: TypeAlias = str | int | bool
Attributes: TypeAlias = Mapping[str, AttributeValue]
_KEY = re.compile(r"^[a-z0-9][a-z0-9_.-]{0,63}$")
_SENSITIVE = (
    "secret",
    "password",
    "passwd",
    "token",
    "api_key",
    "apikey",
    "authorization",
    "cookie",
    "credential",
)


class FrozenAttributes(Mapping[str, AttributeValue]):
    """Read-only scalar attributes with deterministic key iteration."""

    __slots__ = ("_data",)

    def __init__(self, values: Mapping[str, AttributeValue] | None = None) -> None:
        copied = dict(values or {})
        self._data: Mapping[str, AttributeValue] = MappingProxyType(copied)

    def __getitem__(self, key: str) -> AttributeValue:
        return self._data[key]

    def __iter__(self) -> Iterator[str]:
        return iter(sorted(self._data))

    def __len__(self) -> int:
        return len(self._data)

    def __hash__(self) -> int:
        # Python object hashes are process-local. Cross-runtime identity is
        # provided by canonical/event digests, not ``hash(...)``.
        return hash(tuple(sorted(self._data.items())))

    def __repr__(self) -> str:
        return f"FrozenAttributes({dict(self._data)!r})"


def validate_attributes(attributes: Mapping[str, object]) -> FrozenAttributes:
    """Copy and validate producer attributes into immutable canonical state."""
    if len(attributes) > 32:
        raise ObservabilityError("attributes may contain at most 32 keys")
    validated: dict[str, AttributeValue] = {}
    for key, value in attributes.items():
        if not isinstance(key, str) or not _KEY.fullmatch(key):
            raise ObservabilityError(f"invalid attribute key: {key!r}")
        lowered = key.lower()
        if any(marker in lowered for marker in _SENSITIVE):
            raise ObservabilityError(f"sensitive attribute key is forbidden: {key!r}")
        if not isinstance(value, (str, int, bool)):
            raise ObservabilityError(f"attribute {key!r} must be string, integer, or boolean")
        if isinstance(value, str) and len(value) > 512:
            raise ObservabilityError(f"attribute {key!r} exceeds 512 characters")
        if (
            isinstance(value, int)
            and not isinstance(value, bool)
            and not MIN_JSON_SAFE_INTEGER <= value <= MAX_JSON_SAFE_INTEGER
        ):
            raise ObservabilityError(f"attribute {key!r} exceeds the JSON safe-integer range")
        validated[key] = value
    return FrozenAttributes(validated)
