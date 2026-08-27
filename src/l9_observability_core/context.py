"""Trace and execution correlation models."""

from __future__ import annotations

from pydantic import model_validator

from .base import ObservationModel
from .primitives import Identifier


class TraceContext(ObservationModel):
    trace_id: Identifier
    span_id: Identifier
    parent_span_id: Identifier | None = None

    @model_validator(mode="after")
    def reject_self_parent(self) -> TraceContext:
        if self.parent_span_id == self.span_id:
            raise ValueError("parent_span_id must not equal span_id")
        return self


class ExecutionContext(ObservationModel):
    component: Identifier
    operation: Identifier
    program_id: Identifier | None = None
    campaign_id: Identifier | None = None
    task_id: Identifier | None = None
    run_id: Identifier | None = None
    attempt_id: Identifier | None = None
    session_id: Identifier | None = None
    phase: Identifier | None = None
