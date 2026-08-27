"""Cross-event validation helpers."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from .errors import ObservabilityError
from .events import AttemptEvent, ObservabilityEvent

_STABLE_ATTEMPT_COORDINATES = (
    "component",
    "operation",
    "program_id",
    "campaign_id",
    "task_id",
    "run_id",
)


def validate_attempt_chain(events: Iterable[AttemptEvent]) -> None:
    ordered = sorted(events, key=lambda event: event.attempt_number)
    if not ordered:
        return

    expected = 1
    prior_id: str | None = None
    first = ordered[0]
    baseline_trace = first.trace.trace_id
    baseline_execution: dict[str, Any] = {
        field: getattr(first.execution, field) for field in _STABLE_ATTEMPT_COORDINATES
    }
    seen_attempt_ids: set[str] = set()

    for event in ordered:
        if event.attempt_number != expected:
            raise ObservabilityError("attempt chain must be contiguous and 1-indexed")
        if event.attempt_id in seen_attempt_ids:
            raise ObservabilityError(f"duplicate attempt_id: {event.attempt_id}")
        if event.trace.trace_id != baseline_trace:
            raise ObservabilityError("attempt chain must share one trace_id")
        for field, expected_value in baseline_execution.items():
            if getattr(event.execution, field) != expected_value:
                raise ObservabilityError(f"attempt chain execution coordinate changed: {field}")
        if expected == 1:
            if event.prior_attempt_id is not None:
                raise ObservabilityError("first attempt cannot reference a prior attempt")
        elif event.prior_attempt_id != prior_id:
            raise ObservabilityError("attempt prior_attempt_id does not match preceding attempt")
        seen_attempt_ids.add(event.attempt_id)
        prior_id = event.attempt_id
        expected += 1


def require_unique_event_ids(events: Iterable[ObservabilityEvent]) -> None:
    seen: set[str] = set()
    for event in events:
        if event.event_id in seen:
            raise ObservabilityError(f"duplicate event_id: {event.event_id}")
        seen.add(event.event_id)
