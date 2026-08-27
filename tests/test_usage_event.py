from __future__ import annotations

import pytest
from pydantic import ValidationError

from l9_observability_core import CostUsage, TokenUsage, UsageEvent

from .helpers import NOW, execution, trace


def test_usage_exact_integer_cost() -> None:
    event = UsageEvent(
        event_id="evt-u",
        occurred_at=NOW,
        trace=trace(),
        execution=execution(),
        provider="openai",
        model="gpt",
        tokens=TokenUsage(input_tokens=10, output_tokens=5, total_tokens=15),
        cost=CostUsage(currency="USD", amount_microunits=1234),
    )
    assert event.cost and event.cost.amount_microunits == 1234


def test_optional_provider_token_dimensions_preserve_unknown_vs_zero() -> None:
    unknown = TokenUsage(input_tokens=10, output_tokens=5, total_tokens=15)
    observed_zero = TokenUsage(
        input_tokens=10,
        output_tokens=5,
        total_tokens=15,
        cache_read_tokens=0,
    )
    assert unknown.cache_read_tokens is None
    assert observed_zero.cache_read_tokens == 0


def test_token_counts_do_not_coerce_strings() -> None:
    with pytest.raises(ValueError):
        TokenUsage(input_tokens="10", output_tokens=5, total_tokens=15)  # type: ignore[arg-type]


def test_cost_usage_requires_explicit_currency() -> None:
    with pytest.raises(ValidationError):
        CostUsage(amount_microunits=1)  # type: ignore[call-arg]
