"""Time-domain invariant helpers."""

from __future__ import annotations

import re
from datetime import UTC, datetime

from .errors import ObservabilityError
from .primitives import MAX_JSON_SAFE_INTEGER

_MICROSECONDS_PER_DAY = 86_400_000_000
_RFC3339_MICROSECOND = re.compile(
    r"^\d{4}-\d{2}-\d{2}[Tt]\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?(?:[Zz]|[+-]\d{2}:\d{2})$"
)


def require_timestamp_input(value: object, field: str) -> datetime | str:
    """Reject non-wire datetime coercions before Pydantic parses them.

    Programmatic producers may pass an aware ``datetime``. Wire producers must
    pass RFC 3339 text with an explicit timezone and no more precision than the
    microseconds preserved by Python's canonical datetime representation.
    """
    if isinstance(value, datetime):
        return value
    if not isinstance(value, str) or not _RFC3339_MICROSECOND.fullmatch(value):
        raise ObservabilityError(
            f"{field} must be an RFC 3339 timestamp with explicit timezone "
            "and at most 6 fractional digits"
        )
    return value


def require_aware(value: datetime, field: str) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ObservabilityError(f"{field} must be timezone-aware")
    return value


def elapsed_milliseconds(started_at: datetime, completed_at: datetime) -> int:
    """Return floor elapsed whole milliseconds using integer arithmetic only."""
    require_aware(started_at, "started_at")
    require_aware(completed_at, "completed_at")
    # Convert to UTC before ordering/subtraction. Python deliberately ignores
    # UTC-offset differences when two aware datetimes share the same tzinfo
    # object, which otherwise produces incorrect elapsed time across DST folds.
    started_utc = started_at.astimezone(UTC)
    completed_utc = completed_at.astimezone(UTC)
    if completed_utc < started_utc:
        raise ObservabilityError("completed_at must be >= started_at")
    delta = completed_utc - started_utc
    total_microseconds = (
        delta.days * _MICROSECONDS_PER_DAY + delta.seconds * 1_000_000 + delta.microseconds
    )
    duration_ms = total_microseconds // 1_000
    if duration_ms > MAX_JSON_SAFE_INTEGER:
        raise ObservabilityError("elapsed duration exceeds the JSON safe-integer range")
    return duration_ms


def validate_interval(started_at: datetime, completed_at: datetime, duration_ms: int) -> None:
    calculated = elapsed_milliseconds(started_at, completed_at)
    if calculated != duration_ms:
        raise ObservabilityError(
            f"duration_ms mismatch: supplied={duration_ms}, calculated={calculated}"
        )
