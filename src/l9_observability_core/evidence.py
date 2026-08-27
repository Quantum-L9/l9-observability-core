"""External evidence references."""

from __future__ import annotations

import re

from pydantic import Field, field_validator

from .base import ObservationModel
from .enums import EvidenceKind
from .primitives import Identifier

_DIGEST = re.compile(r"^sha256:[a-f0-9]{64}$")


class EvidenceRef(ObservationModel):
    kind: EvidenceKind
    ref: str = Field(min_length=1, max_length=2048)
    digest: str | None = None
    revision: Identifier | None = None
    media_type: str | None = Field(default=None, min_length=1, max_length=255)

    @field_validator("ref")
    @classmethod
    def validate_ref(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("evidence ref must contain a non-whitespace character")
        return value

    @field_validator("digest")
    @classmethod
    def validate_digest(cls, value: str | None) -> str | None:
        if value is not None and not _DIGEST.fullmatch(value):
            raise ValueError("digest must use canonical sha256:<64 lowercase hex> form")
        return value
