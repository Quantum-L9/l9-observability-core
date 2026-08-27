from __future__ import annotations

import pytest

from l9_observability_core import FailureClass, FailureEvent

from .helpers import NOW, execution, trace


def test_failure_event() -> None:
    event = FailureEvent(
        event_id="evt-f",
        occurred_at=NOW,
        trace=trace(),
        execution=execution(),
        failure_class=FailureClass.TIMEOUT,
        failure_code="TOOL_TIMEOUT",
        retryable=True,
    )
    assert event.retryable is True


def test_failure_rejects_self_causation() -> None:
    with pytest.raises(ValueError):
        FailureEvent(
            event_id="evt-f",
            occurred_at=NOW,
            trace=trace(),
            execution=execution(),
            failure_class=FailureClass.INTERNAL,
            failure_code="X",
            retryable=False,
            causal_event_refs=("evt-f",),
        )


def test_retryable_does_not_coerce_integer_to_bool() -> None:
    with pytest.raises(ValueError):
        FailureEvent(
            event_id="evt-f",
            occurred_at=NOW,
            trace=trace(),
            execution=execution(),
            failure_class=FailureClass.INTERNAL,
            failure_code="X",
            retryable=1,  # type: ignore[arg-type]
        )


def test_causal_event_refs_reject_unordered_or_one_shot_iterables() -> None:
    common = dict(
        event_id="failure-ordering",
        occurred_at=NOW,
        trace=trace(),
        execution=execution(),
        failure_class=FailureClass.INTERNAL,
        failure_code="ordering",
        retryable=False,
    )
    with pytest.raises(ValueError, match="ordered list or tuple"):
        FailureEvent(**common, causal_event_refs={"cause-a", "cause-b"})  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="ordered list or tuple"):
        FailureEvent(**common, causal_event_refs=(x for x in ("cause-a", "cause-b")))  # type: ignore[arg-type]
