from __future__ import annotations

import pytest

from l9_observability_core import AttemptEvent, EventStatus, validate_attempt_chain
from l9_observability_core.errors import ObservabilityError

from .helpers import NOW, execution, trace


def make(
    n: int,
    aid: str,
    prior: str | None = None,
    *,
    trace_id: str = "trace-1",
    run_id: str = "run-1",
) -> AttemptEvent:
    return AttemptEvent(
        event_id=f"evt-{n}-{aid}",
        occurred_at=NOW,
        trace=type(trace())(trace_id=trace_id, span_id=f"s-{n}-{aid}"),
        execution=execution(attempt_id=aid, run_id=run_id),
        attempt_id=aid,
        attempt_number=n,
        prior_attempt_id=prior,
        status=EventStatus.COMPLETED,
    )


def test_attempt_chain() -> None:
    validate_attempt_chain([make(1, "a-1"), make(2, "a-2", "a-1")])


def test_retry_requires_prior() -> None:
    with pytest.raises(ValueError):
        make(2, "a-2")


def test_first_attempt_rejects_retry_reason() -> None:
    with pytest.raises(ValueError):
        AttemptEvent(
            event_id="evt-1",
            occurred_at=NOW,
            trace=trace(),
            execution=execution(attempt_id="a-1"),
            attempt_id="a-1",
            attempt_number=1,
            retry_reason="retrying",
            status=EventStatus.FAILED,
        )


def test_attempt_cannot_reference_itself() -> None:
    with pytest.raises(ValueError):
        make(2, "a-2", "a-2")


def test_attempt_chain_rejects_cross_trace_or_run_drift() -> None:
    with pytest.raises(ObservabilityError):
        validate_attempt_chain([make(1, "a-1"), make(2, "a-2", "a-1", trace_id="trace-2")])
    with pytest.raises(ObservabilityError):
        validate_attempt_chain([make(1, "a-1"), make(2, "a-2", "a-1", run_id="run-2")])
