from l9_observability_core import ToolCallEvent, ToolOutcome

from .helpers import NOW, execution, trace


def test_tool_call_event() -> None:
    event = ToolCallEvent(
        event_id="evt-tool",
        occurred_at=NOW,
        trace=trace(),
        execution=execution(),
        tool="github",
        action="fetch",
        outcome=ToolOutcome.COMPLETED,
        duration_ms=12,
    )
    assert event.duration_ms == 12
