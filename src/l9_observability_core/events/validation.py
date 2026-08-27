from __future__ import annotations

from typing import Literal

from pydantic import Field, model_validator

from ..enums import ValidationOutcome
from ..primitives import Identifier, NonNegativeInteger
from .base import ObservabilityEvent


class ValidationEvent(ObservabilityEvent):
    schema_id: Literal["l9.observability.validation-event.v1"] = Field(
        default="l9.observability.validation-event.v1", alias="schema"
    )
    event_type: Literal["validation"] = "validation"
    validator: Identifier
    outcome: ValidationOutcome
    failure_count: NonNegativeInteger
    summary: str | None = Field(default=None, min_length=1, max_length=1024)

    @model_validator(mode="after")
    def validate_failure_count(self) -> ValidationEvent:
        if self.outcome in (ValidationOutcome.PASS, ValidationOutcome.NOT_RUN):
            if self.failure_count != 0:
                raise ValueError(f"{self.outcome.value} validation must have failure_count=0")
        elif self.outcome is ValidationOutcome.FAIL and self.failure_count < 1:
            raise ValueError("fail validation must have failure_count>=1")
        return self
