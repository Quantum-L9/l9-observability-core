"""Canonical scalar primitives shared by typed observation models."""

from __future__ import annotations

import re
from typing import Annotated, TypeAlias

from pydantic import Field, StrictInt, StringConstraints

MAX_JSON_SAFE_INTEGER = 9_007_199_254_740_991
MIN_JSON_SAFE_INTEGER = -MAX_JSON_SAFE_INTEGER

Identifier: TypeAlias = Annotated[
    str,
    StringConstraints(
        min_length=1,
        max_length=256,
        pattern=r"^[A-Za-z0-9][A-Za-z0-9._:/-]*$",
    ),
]
NonNegativeInteger: TypeAlias = Annotated[
    StrictInt,
    Field(ge=0, le=MAX_JSON_SAFE_INTEGER),
]
PositiveInteger: TypeAlias = Annotated[
    StrictInt,
    Field(ge=1, le=MAX_JSON_SAFE_INTEGER),
]

_IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]{0,255}$")


def validate_identifier(value: str | None) -> str | None:
    """Validate the portable L9 identifier grammar without coercion."""
    if value is None:
        return None
    if not isinstance(value, str) or not _IDENTIFIER.fullmatch(value):
        raise ValueError("identifier must use the canonical portable token grammar")
    return value
