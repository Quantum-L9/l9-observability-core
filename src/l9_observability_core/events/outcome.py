from __future__ import annotations

from typing import Literal

from pydantic import Field, StrictBool

from ..enums import EffectivenessSignal, OutcomeKind
from ..evidence import EvidenceRef
from .base import ObservabilityEvent


class OutcomeEvent(ObservabilityEvent):
    schema_id: Literal["l9.observability.outcome-event.v1"] = Field(
        default="l9.observability.outcome-event.v1", alias="schema"
    )
    event_type: Literal["outcome"] = "outcome"
    outcome_kind: OutcomeKind
    success: StrictBool
    effectiveness_signal: EffectivenessSignal
    result_ref: EvidenceRef | None = None
    summary: str | None = Field(default=None, min_length=1, max_length=1024)
