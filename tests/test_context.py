from __future__ import annotations

import pytest

from l9_observability_core import TraceContext, validate_parent_child
from l9_observability_core.errors import ObservabilityError


def test_parent_child_correlation() -> None:
    parent = TraceContext(trace_id="t-1", span_id="s-1")
    child = TraceContext(trace_id="t-1", span_id="s-2", parent_span_id="s-1")
    validate_parent_child(parent, child)


def test_cross_trace_parent_rejected() -> None:
    parent = TraceContext(trace_id="t-1", span_id="s-1")
    child = TraceContext(trace_id="t-2", span_id="s-2", parent_span_id="s-1")
    with pytest.raises(ObservabilityError):
        validate_parent_child(parent, child)


def test_span_cannot_parent_itself() -> None:
    with pytest.raises(ValueError):
        TraceContext(trace_id="t-1", span_id="s-1", parent_span_id="s-1")
