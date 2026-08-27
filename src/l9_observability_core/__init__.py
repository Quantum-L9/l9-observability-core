"""Canonical L9 observability domain contracts."""

from .attributes import FrozenAttributes
from .canonical import canonical_bytes, canonical_dict, canonical_json, sha256_digest
from .context import ExecutionContext, TraceContext
from .correlation import validate_parent_child
from .enums import (
    EffectivenessSignal,
    EventStatus,
    EvidenceKind,
    FailureClass,
    OutcomeKind,
    SpanKind,
    ToolOutcome,
    ValidationOutcome,
)
from .errors import CanonicalizationError, ObservabilityError, UnknownSchemaError
from .events import (
    AttemptEvent,
    ExecutionSpan,
    FailureEvent,
    ObservabilityEvent,
    OutcomeEvent,
    ToolCallEvent,
    UsageEvent,
    ValidationEvent,
)
from .evidence import EvidenceRef
from .primitives import MAX_JSON_SAFE_INTEGER, MIN_JSON_SAFE_INTEGER
from .registry import REGISTRY, canonical_event_json, event_digest, normalize_event, parse_event
from .timing import elapsed_milliseconds
from .usage import CostUsage, TokenUsage
from .validation import require_unique_event_ids, validate_attempt_chain

__all__ = [
    "AttemptEvent",
    "CanonicalizationError",
    "CostUsage",
    "EffectivenessSignal",
    "EventStatus",
    "EvidenceKind",
    "EvidenceRef",
    "ExecutionContext",
    "ExecutionSpan",
    "FailureClass",
    "FailureEvent",
    "FrozenAttributes",
    "MAX_JSON_SAFE_INTEGER",
    "MIN_JSON_SAFE_INTEGER",
    "ObservabilityError",
    "ObservabilityEvent",
    "OutcomeEvent",
    "OutcomeKind",
    "REGISTRY",
    "SpanKind",
    "TokenUsage",
    "ToolCallEvent",
    "ToolOutcome",
    "TraceContext",
    "UnknownSchemaError",
    "UsageEvent",
    "ValidationEvent",
    "ValidationOutcome",
    "canonical_bytes",
    "canonical_dict",
    "canonical_json",
    "canonical_event_json",
    "elapsed_milliseconds",
    "event_digest",
    "normalize_event",
    "parse_event",
    "require_unique_event_ids",
    "sha256_digest",
    "validate_attempt_chain",
    "validate_parent_child",
]
