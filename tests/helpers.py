from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from l9_observability_core import ExecutionContext, TraceContext

NOW = datetime(2026, 8, 23, 21, 0, 0, tzinfo=UTC)
LATER = datetime(2026, 8, 23, 21, 0, 1, tzinfo=UTC)


def trace(span: str = "span-1", parent: str | None = None) -> TraceContext:
    return TraceContext(trace_id="trace-1", span_id=span, parent_span_id=parent)


def execution(**overrides: Any) -> ExecutionContext:
    data: dict[str, Any] = {
        "component": "l9-cognitive-runtime",
        "operation": "compile",
        "run_id": "run-1",
    }
    data.update(overrides)
    return ExecutionContext(**data)
