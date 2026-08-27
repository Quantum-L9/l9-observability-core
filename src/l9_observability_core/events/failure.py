from __future__ import annotations

from typing import Literal

from pydantic import Field, StrictBool, field_validator, model_validator

from ..enums import FailureClass
from ..primitives import Identifier
from .base import ObservabilityEvent


class FailureEvent(ObservabilityEvent):
    schema_id: Literal["l9.observability.failure-event.v1"] = Field(
        default="l9.observability.failure-event.v1", alias="schema"
    )
    event_type: Literal["failure"] = "failure"
    failure_class: FailureClass
    failure_code: Identifier
    retryable: StrictBool
    causal_event_refs: tuple[Identifier, ...] = ()
    message: str | None = Field(default=None, min_length=1, max_length=2048)

    @field_validator("causal_event_refs", mode="before")
    @classmethod
    def require_ordered_causal_refs(cls, value: object) -> object:
        if not isinstance(value, (list, tuple)):
            raise ValueError("causal_event_refs must be supplied as an ordered list or tuple")
        return value

    @model_validator(mode="after")
    def validate_causal_refs(self) -> FailureEvent:
        if len(self.causal_event_refs) != len(set(self.causal_event_refs)):
            raise ValueError("causal_event_refs must be unique")
        if self.event_id in self.causal_event_refs:
            raise ValueError("failure event must not cite itself as a causal event")
        return self
