from __future__ import annotations

from typing import Literal

from pydantic import Field

from ..primitives import Identifier
from ..usage import CostUsage, TokenUsage
from .base import ObservabilityEvent


class UsageEvent(ObservabilityEvent):
    schema_id: Literal["l9.observability.usage-event.v1"] = Field(
        default="l9.observability.usage-event.v1", alias="schema"
    )
    event_type: Literal["usage"] = "usage"
    provider: Identifier
    model: Identifier
    tokens: TokenUsage
    cost: CostUsage | None = None
