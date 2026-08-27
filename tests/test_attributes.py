from __future__ import annotations

import pytest

from l9_observability_core import MAX_JSON_SAFE_INTEGER, EventStatus, ExecutionSpan, SpanKind
from l9_observability_core.attributes import validate_attributes
from l9_observability_core.errors import ObservabilityError

from .helpers import LATER, NOW, execution, trace


def test_bounded_scalar_attributes() -> None:
    assert validate_attributes({"repo": "l9", "attempt": 2, "cached": True})["attempt"] == 2


def test_attribute_iteration_is_deterministic() -> None:
    attributes = validate_attributes({"z": 1, "a": 2, "m": 3})
    assert list(attributes) == ["a", "m", "z"]


def test_sensitive_attribute_key_rejected() -> None:
    with pytest.raises(ObservabilityError):
        validate_attributes({"api_key": "nope"})


def test_nested_attribute_rejected() -> None:
    with pytest.raises(ObservabilityError):
        validate_attributes({"payload": {"x": 1}})


def test_unsafe_integer_attribute_rejected() -> None:
    with pytest.raises(ObservabilityError):
        validate_attributes({"count": MAX_JSON_SAFE_INTEGER + 1})


def test_event_attributes_are_defensively_copied_and_immutable() -> None:
    source = {"repo": "l9"}
    event = ExecutionSpan(
        event_id="evt-immutable",
        occurred_at=LATER,
        trace=trace(),
        execution=execution(),
        attributes=source,
        started_at=NOW,
        completed_at=LATER,
        duration_ms=1000,
        span_kind=SpanKind.INTERNAL,
        status=EventStatus.COMPLETED,
    )
    source["repo"] = "changed"
    assert event.attributes["repo"] == "l9"
    with pytest.raises(TypeError):
        event.attributes["repo"] = "mutated"  # type: ignore[index]
