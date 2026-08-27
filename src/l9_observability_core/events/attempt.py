from __future__ import annotations

from typing import Literal

from pydantic import Field, model_validator

from ..enums import EventStatus
from ..primitives import Identifier, PositiveInteger
from .base import ObservabilityEvent


class AttemptEvent(ObservabilityEvent):
    schema_id: Literal["l9.observability.attempt-event.v1"] = Field(
        default="l9.observability.attempt-event.v1", alias="schema"
    )
    event_type: Literal["attempt"] = "attempt"
    attempt_id: Identifier
    attempt_number: PositiveInteger
    prior_attempt_id: Identifier | None = None
    retry_reason: str | None = Field(default=None, min_length=1, max_length=512)
    status: EventStatus

    @model_validator(mode="after")
    def validate_attempt(self) -> AttemptEvent:
        if self.attempt_number == 1:
            if self.prior_attempt_id is not None:
                raise ValueError("attempt 1 must not declare prior_attempt_id")
            if self.retry_reason is not None:
                raise ValueError("attempt 1 must not declare retry_reason")
        elif self.prior_attempt_id is None:
            raise ValueError("retry attempts must declare prior_attempt_id")
        if self.prior_attempt_id == self.attempt_id:
            raise ValueError("prior_attempt_id must not equal attempt_id")
        if self.execution.attempt_id is not None and self.execution.attempt_id != self.attempt_id:
            raise ValueError("execution.attempt_id must equal attempt_id when supplied")
        return self
