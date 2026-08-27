from l9_observability_core import EventStatus, ExecutionSpan, SpanKind

from .helpers import LATER, NOW, execution, trace


def test_schema_alias_is_wire_key() -> None:
    event = ExecutionSpan(
        event_id="evt-alias",
        occurred_at=LATER,
        trace=trace(),
        execution=execution(),
        started_at=NOW,
        completed_at=LATER,
        duration_ms=1000,
        span_kind=SpanKind.INTERNAL,
        status=EventStatus.COMPLETED,
    )
    wire = event.to_wire_dict()
    assert wire["schema"] == "l9.observability.execution-span.v1"
    assert "schema_id" not in wire
