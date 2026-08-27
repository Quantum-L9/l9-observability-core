"""Exact usage accounting models."""

from __future__ import annotations

from pydantic import field_validator

from .base import ObservationModel
from .primitives import NonNegativeInteger


class TokenUsage(ObservationModel):
    input_tokens: NonNegativeInteger
    output_tokens: NonNegativeInteger
    total_tokens: NonNegativeInteger
    cache_read_tokens: NonNegativeInteger | None = None
    cache_write_tokens: NonNegativeInteger | None = None
    reasoning_tokens: NonNegativeInteger | None = None


class CostUsage(ObservationModel):
    currency: str
    amount_microunits: NonNegativeInteger

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, value: str) -> str:
        if len(value) != 3 or not value.isascii() or not value.isalpha() or value.upper() != value:
            raise ValueError("currency must be three uppercase ASCII letters")
        return value
