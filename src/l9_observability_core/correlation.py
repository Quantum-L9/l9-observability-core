"""Pure correlation helpers."""

from .context import TraceContext
from .errors import ObservabilityError


def validate_parent_child(parent: TraceContext, child: TraceContext) -> None:
    if parent.trace_id != child.trace_id:
        raise ObservabilityError("parent and child must share trace_id")
    if child.parent_span_id != parent.span_id:
        raise ObservabilityError("child.parent_span_id must equal parent.span_id")
