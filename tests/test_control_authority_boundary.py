"""This library holds no control authority, and must not acquire any.

`l9-observability-core` owns event contracts, canonical digests, and
correlation validation. It does not schedule, gate, admit, dispatch, retry, or
mutate. That boundary is currently clean -- the package is frozen dataclasses,
canonicalisation, digesting, and validators -- but "clean today" is not a
guarantee, and the library is unconsumed, so nothing downstream would notice a
control verb appearing here.

Backing INVARIANTS.md product invariants 2 and 4 with an executable check makes
the boundary a gate rather than a description.
"""

from __future__ import annotations

import inspect

import l9_observability_core as package

# Verbs that would make this library a control plane rather than a contract
# library. `retry` is included deliberately: recording that a retry happened is
# a contract concern, owning the decision to retry is not -- see
# `test_retry_appears_only_as_descriptive_event_fields`.
CONTROL_VERBS = (
    "schedule",
    "dispatch",
    "route",
    "gate",
    "admit",
    "retry",
    "mutate",
    "execute",
    "publish",
    "emit",
    "send",
    "enqueue",
    "poll",
)


def test_public_api_exposes_no_control_verb() -> None:
    offenders = [
        name
        for name in package.__all__
        for verb in CONTROL_VERBS
        if verb in name.lower() and callable(getattr(package, name, None))
    ]
    assert offenders == [], f"control-plane callables in the public API: {offenders}"


def test_public_callables_are_pure_contract_operations() -> None:
    """Every exported callable is canonicalisation, parsing, or validation.

    A new export outside these families is the shape a control verb would
    arrive in, so it has to be added here deliberately.
    """
    allowed_prefixes = (
        "canonical_",
        "normalize_",
        "parse_",
        "validate_",
        "require_",
        "sha256_",
        "event_",
        "elapsed_",
    )
    callables = [
        name
        for name in package.__all__
        if callable(getattr(package, name)) and not inspect.isclass(getattr(package, name))
    ]
    assert callables, "expected exported callables"
    unexpected = [name for name in callables if not name.startswith(allowed_prefixes)]
    assert unexpected == [], f"unclassified exported callables: {unexpected}"


def test_retry_appears_only_as_descriptive_event_fields() -> None:
    """Describing a retry is a contract concern; deciding one is not.

    `AttemptEvent.retry_reason` and `FailureEvent.retryable` record what a
    producer observed. Neither makes this library the owner of retry policy,
    and no callable may imply otherwise.
    """
    assert "retry_reason" in package.AttemptEvent.model_fields
    assert "retryable" in package.FailureEvent.model_fields
    retry_callables = [
        name
        for name in package.__all__
        if "retry" in name.lower() and callable(getattr(package, name, None))
    ]
    assert retry_callables == []
