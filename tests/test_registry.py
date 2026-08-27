from __future__ import annotations

from typing import Literal

import pytest
from pydantic import Field, ValidationError

from l9_observability_core import (
    REGISTRY,
    EventStatus,
    ExecutionSpan,
    SpanKind,
    event_digest,
    parse_event,
)
from l9_observability_core.errors import ObservabilityError, UnknownSchemaError
from l9_observability_core.events.base import ObservabilityEvent

from .helpers import LATER, NOW, execution, trace


def test_registry_roundtrip() -> None:
    event = ExecutionSpan(
        event_id="evt-r",
        occurred_at=LATER,
        trace=trace(),
        execution=execution(),
        started_at=NOW,
        completed_at=LATER,
        duration_ms=1000,
        span_kind=SpanKind.INTERNAL,
        status=EventStatus.COMPLETED,
    )
    parsed = parse_event(event.model_dump(mode="python", by_alias=True))
    assert parsed == event


def test_unknown_or_malformed_schema_fails_closed() -> None:
    with pytest.raises(UnknownSchemaError):
        parse_event({"schema": "future.v99"})
    with pytest.raises(UnknownSchemaError):
        parse_event({"schema": ["not", "hashable"]})  # type: ignore[dict-item]


def test_registry_is_read_only() -> None:
    with pytest.raises(TypeError):
        REGISTRY["future.v99"] = ExecutionSpan  # type: ignore[index]


def test_wire_parser_requires_explicit_event_type() -> None:
    event = ExecutionSpan(
        event_id="evt-r2",
        occurred_at=LATER,
        trace=trace(),
        execution=execution(),
        started_at=NOW,
        completed_at=LATER,
        duration_ms=1000,
        span_kind=SpanKind.INTERNAL,
        status=EventStatus.COMPLETED,
    )
    payload = event.to_wire_dict()
    payload.pop("event_type")
    with pytest.raises(ObservabilityError, match="event_type"):
        parse_event(payload)


def test_event_digest_revalidates_claimed_registered_schema() -> None:
    class SpoofExecutionSpan(ObservabilityEvent):
        schema_id: Literal["l9.observability.execution-span.v1"] = Field(
            default="l9.observability.execution-span.v1", alias="schema"
        )
        event_type: Literal["execution_span"] = "execution_span"

    spoof = SpoofExecutionSpan(
        event_id="evt-spoof",
        occurred_at=LATER,
        trace=trace(),
        execution=execution(),
    )
    with pytest.raises(ValidationError):
        event_digest(spoof)
