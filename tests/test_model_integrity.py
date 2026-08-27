from __future__ import annotations

from datetime import UTC

import pytest

from l9_observability_core import EventStatus, ExecutionSpan, SpanKind

from .helpers import LATER, NOW, execution, trace


def test_model_copy_revalidates_updates() -> None:
    event = ExecutionSpan(
        event_id="evt-copy",
        occurred_at=LATER,
        trace=trace(),
        execution=execution(),
        started_at=NOW,
        completed_at=LATER,
        duration_ms=1000,
        span_kind=SpanKind.INTERNAL,
        status=EventStatus.COMPLETED,
    )
    with pytest.raises(ValueError):
        event.model_copy(update={"duration_ms": "1000"})
    with pytest.raises(ValueError):
        event.model_copy(update={"duration_ms": 999})


def test_event_evidence_refs_are_immutable_and_unique() -> None:
    from datetime import datetime

    import pytest
    from pydantic import ValidationError

    from l9_observability_core import (
        EventStatus,
        EvidenceKind,
        EvidenceRef,
        ExecutionContext,
        ExecutionSpan,
        SpanKind,
        TraceContext,
    )

    evidence = EvidenceRef(kind=EvidenceKind.RECEIPT, ref="receipt:1")
    event = ExecutionSpan(
        event_id="evt-1",
        occurred_at=datetime(2026, 8, 23, tzinfo=UTC),
        trace=TraceContext(trace_id="trace-1", span_id="span-1"),
        execution=ExecutionContext(component="cog", operation="compile"),
        evidence_refs=(evidence,),
        started_at=datetime(2026, 8, 23, tzinfo=UTC),
        completed_at=datetime(2026, 8, 23, tzinfo=UTC),
        duration_ms=0,
        span_kind=SpanKind.INTERNAL,
        status=EventStatus.COMPLETED,
    )

    assert isinstance(event.evidence_refs, tuple)
    with pytest.raises(ValidationError):
        event.model_copy(update={"evidence_refs": (evidence, evidence)})


def test_model_copy_valid_update_remains_validated_model() -> None:
    from l9_observability_core import ExecutionContext

    original = ExecutionContext(component="cog", operation="compile")
    copied = original.model_copy(update={"operation": "plan"})
    assert copied.operation == "plan"
    assert original.operation == "compile"


def test_model_copy_deep_handles_immutable_attribute_mapping() -> None:
    event = ExecutionSpan(
        event_id="evt-deep-copy",
        occurred_at=LATER,
        trace=trace(),
        execution=execution(),
        attributes={"b": 2, "a": 1},
        started_at=NOW,
        completed_at=LATER,
        duration_ms=1000,
        span_kind=SpanKind.INTERNAL,
        status=EventStatus.COMPLETED,
    )
    copied = event.model_copy(deep=True)
    assert copied == event
    assert copied is not event
    assert copied.attributes is not event.attributes


def test_binary_values_are_not_silently_coerced_to_text() -> None:
    from l9_observability_core import EvidenceRef, TraceContext

    with pytest.raises(ValueError, match="binary values are forbidden"):
        TraceContext(trace_id=b"trace", span_id="span")  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="binary values are forbidden"):
        EvidenceRef(kind=b"artifact", ref="artifact:1")  # type: ignore[arg-type]


def test_model_copy_rejects_binary_text_coercion() -> None:
    from l9_observability_core import ExecutionContext

    context = ExecutionContext(component="cog", operation="compile")
    with pytest.raises(ValueError, match="binary values are forbidden"):
        context.model_copy(update={"operation": b"compile"})


def test_evidence_refs_reject_unordered_or_one_shot_iterables() -> None:
    from l9_observability_core import EvidenceKind, EvidenceRef

    evidence = EvidenceRef(kind=EvidenceKind.ARTIFACT, ref="artifact:1")
    common = dict(
        event_id="evt-evidence-order",
        occurred_at=LATER,
        trace=trace(),
        execution=execution(),
        started_at=NOW,
        completed_at=LATER,
        duration_ms=1000,
        span_kind=SpanKind.INTERNAL,
        status=EventStatus.COMPLETED,
    )
    with pytest.raises(ValueError, match="ordered list or tuple"):
        ExecutionSpan(**common, evidence_refs={evidence})  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="ordered list or tuple"):
        ExecutionSpan(**common, evidence_refs=(item for item in (evidence,)))  # type: ignore[arg-type]
