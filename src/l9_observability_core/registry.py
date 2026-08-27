"""Deterministic read-only schema-to-model registry and event normalization helpers."""

from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType
from typing import Any, TypeAlias

from .canonical import canonical_json, sha256_digest
from .errors import ObservabilityError, UnknownSchemaError
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

EventModel: TypeAlias = (
    AttemptEvent
    | ExecutionSpan
    | FailureEvent
    | OutcomeEvent
    | ToolCallEvent
    | UsageEvent
    | ValidationEvent
)
EventModelType: TypeAlias = type[
    AttemptEvent
    | ExecutionSpan
    | FailureEvent
    | OutcomeEvent
    | ToolCallEvent
    | UsageEvent
    | ValidationEvent
]
EventInput: TypeAlias = ObservabilityEvent | Mapping[str, Any]

_REGISTRY: dict[str, EventModelType] = {
    "l9.observability.execution-span.v1": ExecutionSpan,
    "l9.observability.attempt-event.v1": AttemptEvent,
    "l9.observability.tool-call-event.v1": ToolCallEvent,
    "l9.observability.validation-event.v1": ValidationEvent,
    "l9.observability.failure-event.v1": FailureEvent,
    "l9.observability.usage-event.v1": UsageEvent,
    "l9.observability.outcome-event.v1": OutcomeEvent,
}
REGISTRY: Mapping[str, EventModelType] = MappingProxyType(_REGISTRY)


def parse_event(payload: Mapping[str, Any]) -> EventModel:
    """Parse one wire event through its registered canonical model."""
    schema = payload.get("schema")
    if not isinstance(schema, str):
        raise UnknownSchemaError("observability schema must be a string")
    model = REGISTRY.get(schema)
    if model is None:
        raise UnknownSchemaError(f"unknown observability schema: {schema!r}")
    if "event_type" not in payload:
        raise ObservabilityError("wire event must explicitly declare event_type")
    return model.model_validate(dict(payload))


def normalize_event(value: EventInput) -> EventModel:
    """Return a validated canonical event model with defaults materialized."""
    if isinstance(value, ObservabilityEvent):
        # Reparse through the registered model rather than trusting an arbitrary
        # ObservabilityEvent subclass that merely claims a registered schema.
        return parse_event(value.to_wire_dict())
    return parse_event(value)


def canonical_event_json(value: EventInput) -> str:
    """Canonicalize semantic event state after schema/model normalization."""
    return canonical_json(normalize_event(value))


def event_digest(value: EventInput) -> str:
    """Digest semantic event state after schema/model normalization."""
    return sha256_digest(normalize_event(value))
