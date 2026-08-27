import pytest

from l9_observability_core import EventStatus, ExecutionSpan, SpanKind

from .helpers import LATER, NOW, execution, trace


def test_execution_span_validates_duration() -> None:
    event = ExecutionSpan(
        event_id="evt-1",
        occurred_at=LATER,
        trace=trace(),
        execution=execution(),
        started_at=NOW,
        completed_at=LATER,
        duration_ms=1000,
        span_kind=SpanKind.INTERNAL,
        status=EventStatus.COMPLETED,
    )
    assert event.duration_ms == 1000


def test_execution_span_rejects_mismatched_duration() -> None:
    with pytest.raises(ValueError):
        ExecutionSpan(
            event_id="evt-1",
            occurred_at=LATER,
            trace=trace(),
            execution=execution(),
            started_at=NOW,
            completed_at=LATER,
            duration_ms=999,
            span_kind=SpanKind.INTERNAL,
            status=EventStatus.COMPLETED,
        )
