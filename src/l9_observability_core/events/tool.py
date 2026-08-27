from __future__ import annotations

from typing import Literal

from pydantic import Field

from ..enums import ToolOutcome
from ..evidence import EvidenceRef
from ..primitives import Identifier, NonNegativeInteger
from .base import ObservabilityEvent


class ToolCallEvent(ObservabilityEvent):
    schema_id: Literal["l9.observability.tool-call-event.v1"] = Field(
        default="l9.observability.tool-call-event.v1", alias="schema"
    )
    event_type: Literal["tool_call"] = "tool_call"
    tool: Identifier
    action: Identifier
    outcome: ToolOutcome
    duration_ms: NonNegativeInteger
    request_ref: EvidenceRef | None = None
    result_ref: EvidenceRef | None = None
