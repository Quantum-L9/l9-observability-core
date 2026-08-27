from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from l9_observability_core import (
    MAX_JSON_SAFE_INTEGER,
    canonical_json,
    sha256_digest,
)
from l9_observability_core.errors import CanonicalizationError


def test_canonical_key_order_and_digest_stable() -> None:
    left = {"b": 2, "a": 1}
    right = {"a": 1, "b": 2}
    assert canonical_json(left) == '{"a":1,"b":2}'
    assert sha256_digest(left) == sha256_digest(right)


def test_canonical_timestamp_normalizes_to_fixed_utc_microseconds() -> None:
    value = datetime(2026, 8, 23, 17, 0, 0, 123000, tzinfo=timezone(timedelta(hours=-4)))
    assert canonical_json({"at": value}) == '{"at":"2026-08-23T21:00:00.123000Z"}'


def test_canonical_rejects_float_non_string_keys_and_unsafe_integers() -> None:
    with pytest.raises(CanonicalizationError):
        canonical_json({"x": 1.25})
    with pytest.raises(CanonicalizationError):
        canonical_json({1: "x"})
    with pytest.raises(CanonicalizationError):
        canonical_json({"x": MAX_JSON_SAFE_INTEGER + 1})


def test_event_digest_materializes_semantic_defaults() -> None:
    from l9_observability_core import event_digest

    payload_without_defaults = {
        "schema": "l9.observability.validation-event.v1",
        "event_type": "validation",
        "event_id": "evt-defaults",
        "occurred_at": "2026-08-23T21:00:00Z",
        "trace": {"trace_id": "t", "span_id": "s"},
        "execution": {"component": "c", "operation": "o"},
        "validator": "pytest",
        "outcome": "pass",
        "failure_count": 0,
    }
    payload_with_defaults = {
        **payload_without_defaults,
        "trace": {"trace_id": "t", "span_id": "s", "parent_span_id": None},
        "execution": {
            "component": "c",
            "operation": "o",
            "program_id": None,
            "campaign_id": None,
            "task_id": None,
            "run_id": None,
            "attempt_id": None,
            "session_id": None,
            "phase": None,
        },
        "evidence_refs": [],
        "attributes": {},
        "summary": None,
    }
    assert event_digest(payload_without_defaults) == event_digest(payload_with_defaults)
