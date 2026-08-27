from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import Field, ValidationInfo, field_validator, model_validator

from ..enums import EventStatus, SpanKind
from ..primitives import NonNegativeInteger
from ..timing import require_timestamp_input, validate_interval
from .base import ObservabilityEvent


class ExecutionSpan(ObservabilityEvent):
    schema_id: Literal["l9.observability.execution-span.v1"] = Field(
        default="l9.observability.execution-span.v1", alias="schema"
    )
    event_type: Literal["execution_span"] = "execution_span"
    started_at: datetime
    completed_at: datetime
    duration_ms: NonNegativeInteger
    span_kind: SpanKind
    status: EventStatus

    @field_validator("started_at", "completed_at", mode="before")
    @classmethod
    def validate_interval_timestamp_input(cls, value: object, info: ValidationInfo) -> object:
        return require_timestamp_input(value, info.field_name or "")

    @model_validator(mode="after")
    def validate_timing(self) -> ExecutionSpan:
        validate_interval(self.started_at, self.completed_at, self.duration_ms)
        return self
