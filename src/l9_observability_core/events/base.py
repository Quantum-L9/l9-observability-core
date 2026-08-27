"""Shared immutable event envelope."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime

from pydantic import Field, field_serializer, field_validator

from ..attributes import AttributeValue, FrozenAttributes, validate_attributes
from ..base import ObservationModel
from ..context import ExecutionContext, TraceContext
from ..evidence import EvidenceRef
from ..primitives import Identifier
from ..timing import require_aware, require_timestamp_input


class ObservabilityEvent(ObservationModel):
    event_id: Identifier
    occurred_at: datetime
    trace: TraceContext
    execution: ExecutionContext
    evidence_refs: tuple[EvidenceRef, ...] = ()
    attributes: Mapping[str, AttributeValue] = Field(default_factory=FrozenAttributes)

    @field_validator("occurred_at", mode="before")
    @classmethod
    def validate_occurred_at_input(cls, value: object) -> object:
        return require_timestamp_input(value, "occurred_at")

    @field_validator("occurred_at")
    @classmethod
    def validate_occurred_at(cls, value: datetime) -> datetime:
        return require_aware(value, "occurred_at")

    @field_validator("evidence_refs", mode="before")
    @classmethod
    def require_ordered_evidence_refs(cls, value: object) -> object:
        if not isinstance(value, (list, tuple)):
            raise ValueError("evidence_refs must be supplied as an ordered list or tuple")
        return value

    @field_validator("evidence_refs")
    @classmethod
    def validate_evidence_refs(cls, values: tuple[EvidenceRef, ...]) -> tuple[EvidenceRef, ...]:
        keys = [
            (item.kind, item.ref, item.digest, item.revision, item.media_type) for item in values
        ]
        if len(keys) != len(set(keys)):
            raise ValueError("evidence_refs must be unique")
        return values

    @field_validator("attributes", mode="after")
    @classmethod
    def validate_event_attributes(cls, value: Mapping[str, object]) -> FrozenAttributes:
        return validate_attributes(value)

    @field_serializer("attributes")
    def serialize_attributes(
        self, value: Mapping[str, AttributeValue]
    ) -> dict[str, AttributeValue]:
        return dict(value)
