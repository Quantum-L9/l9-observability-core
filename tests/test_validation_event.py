from __future__ import annotations

import pytest

from l9_observability_core import ValidationEvent, ValidationOutcome

from .helpers import NOW, execution, trace


def build(outcome: ValidationOutcome, failure_count: object) -> ValidationEvent:
    return ValidationEvent(
        event_id=f"evt-{outcome.value}",
        occurred_at=NOW,
        trace=trace(),
        execution=execution(),
        validator="pytest",
        outcome=outcome,
        failure_count=failure_count,  # type: ignore[arg-type]
    )


def test_pass_requires_zero_failures() -> None:
    assert build(ValidationOutcome.PASS, 0).failure_count == 0
    with pytest.raises(ValueError):
        build(ValidationOutcome.PASS, 1)


def test_fail_requires_at_least_one_failure() -> None:
    with pytest.raises(ValueError):
        build(ValidationOutcome.FAIL, 0)
    assert build(ValidationOutcome.FAIL, 1).failure_count == 1


def test_not_run_requires_zero_failures() -> None:
    with pytest.raises(ValueError):
        build(ValidationOutcome.NOT_RUN, 1)


def test_integer_fields_do_not_coerce_numeric_strings() -> None:
    with pytest.raises(ValueError):
        build(ValidationOutcome.PASS, "0")
