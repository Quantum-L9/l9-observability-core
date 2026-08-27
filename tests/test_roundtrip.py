from l9_observability_core import (
    AttemptEvent,
    CostUsage,
    EffectivenessSignal,
    EventStatus,
    FailureClass,
    FailureEvent,
    OutcomeEvent,
    OutcomeKind,
    TokenUsage,
    ToolCallEvent,
    ToolOutcome,
    UsageEvent,
    ValidationEvent,
    ValidationOutcome,
    event_digest,
    parse_event,
)

from .helpers import NOW, execution, trace


def test_all_event_families_roundtrip() -> None:
    events = [
        AttemptEvent(
            event_id="a",
            occurred_at=NOW,
            trace=trace("sa"),
            execution=execution(attempt_id="a1"),
            attempt_id="a1",
            attempt_number=1,
            status=EventStatus.COMPLETED,
        ),
        ToolCallEvent(
            event_id="t",
            occurred_at=NOW,
            trace=trace("st"),
            execution=execution(),
            tool="github",
            action="fetch",
            outcome=ToolOutcome.COMPLETED,
            duration_ms=1,
        ),
        ValidationEvent(
            event_id="v",
            occurred_at=NOW,
            trace=trace("sv"),
            execution=execution(),
            validator="pytest",
            outcome=ValidationOutcome.PASS,
            failure_count=0,
        ),
        FailureEvent(
            event_id="f",
            occurred_at=NOW,
            trace=trace("sf"),
            execution=execution(),
            failure_class=FailureClass.INTERNAL,
            failure_code="X",
            retryable=False,
        ),
        UsageEvent(
            event_id="u",
            occurred_at=NOW,
            trace=trace("su"),
            execution=execution(),
            provider="openai",
            model="gpt",
            tokens=TokenUsage(input_tokens=1, output_tokens=1, total_tokens=2),
            cost=CostUsage(currency="USD", amount_microunits=1),
        ),
        OutcomeEvent(
            event_id="o",
            occurred_at=NOW,
            trace=trace("so"),
            execution=execution(),
            outcome_kind=OutcomeKind.COMPLETED,
            success=True,
            effectiveness_signal=EffectivenessSignal.POSITIVE,
        ),
    ]
    for event in events:
        wire = event.to_wire_dict()
        parsed = parse_event(wire)
        assert parsed == event
        assert event_digest(parsed) == event_digest(event)
