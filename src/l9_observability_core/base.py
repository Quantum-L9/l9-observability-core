"""Strict immutable base model and wire helpers."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self

from pydantic import BaseModel, ConfigDict, model_validator


def _reject_binary_inputs(value: Any, *, path: str = "$") -> None:
    """Reject binary-to-text coercion before Pydantic can reinterpret producer input."""
    if isinstance(value, (bytes, bytearray, memoryview)):
        raise ValueError(f"binary values are forbidden in canonical observation input at {path}")
    if isinstance(value, BaseModel):
        return
    if isinstance(value, Mapping):
        for key, item in value.items():
            _reject_binary_inputs(key, path=f"{path}.<key>")
            _reject_binary_inputs(item, path=f"{path}.{key}")
        return
    if isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            _reject_binary_inputs(item, path=f"{path}[{index}]")


class ObservationModel(BaseModel):
    """Base for canonical contracts: frozen, fail-closed, alias-aware."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=False,
        populate_by_name=True,
        validate_default=True,
    )

    @model_validator(mode="before")
    @classmethod
    def reject_binary_input_coercion(cls, value: Any) -> Any:
        _reject_binary_inputs(value)
        return value

    def to_wire_dict(self) -> dict[str, Any]:
        """Return a detached JSON-compatible representation using wire aliases."""
        return self.model_dump(mode="json", by_alias=True)

    def model_copy(
        self,
        *,
        update: Mapping[str, Any] | None = None,
        deep: bool = False,
    ) -> Self:
        """Copy while revalidating updates instead of bypassing canonical invariants."""
        if not update and not deep:
            return super().model_copy(deep=deep)
        payload = self.model_dump(mode="python", by_alias=False)
        if update:
            payload.update(update)
        return self.__class__.model_validate(payload)
