from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import ValidationError as JsonSchemaValidationError
from referencing import Registry, Resource

from l9_observability_core import parse_event, require_unique_event_ids

SCHEMA_DIR = Path(__file__).resolve().parents[1] / "schemas" / "v1"
FIXTURE_DIR = Path(__file__).resolve().parents[1] / "examples" / "fixtures"
BASE = "urn:quantum-l9:observability:v1:"


def load(name: str) -> dict[str, object]:
    return json.loads((SCHEMA_DIR / name).read_text())


def registry() -> Registry:
    resources = []
    for path in SCHEMA_DIR.glob("*.json"):
        schema = json.loads(path.read_text())
        resources.append((schema["$id"], Resource.from_contents(schema)))
    return Registry().with_resources(resources)


def union_validator() -> Draft202012Validator:
    return Draft202012Validator(
        load("observability-event.schema.json"),
        registry=registry(),
        format_checker=FormatChecker(),
    )


def test_all_schemas_are_draft_2020_12_valid() -> None:
    for path in sorted(SCHEMA_DIR.glob("*.json")):
        Draft202012Validator.check_schema(json.loads(path.read_text()))


def test_all_local_schema_ids_are_non_network_urns() -> None:
    for path in sorted(SCHEMA_DIR.glob("*.json")):
        schema = json.loads(path.read_text())
        assert schema["$id"].startswith(BASE)


def test_event_union_lists_every_first_class_event() -> None:
    union = load("observability-event.schema.json")
    refs = {entry["$ref"] for entry in union["oneOf"]}  # type: ignore[index]
    assert refs == {
        BASE + "execution-span",
        BASE + "attempt-event",
        BASE + "tool-call-event",
        BASE + "validation-event",
        BASE + "failure-event",
        BASE + "usage-event",
        BASE + "outcome-event",
    }


def test_cross_consumer_fixtures_validate_and_parse() -> None:
    validator = union_validator()
    parsed_events = []
    for path in sorted(FIXTURE_DIR.glob("*.json")):
        payload = json.loads(path.read_text())
        validator.validate(payload)
        parsed = parse_event(payload)
        parsed_events.append(parsed)
        validator.validate(parsed.to_wire_dict())
    require_unique_event_ids(parsed_events)


def test_fixture_corpus_covers_every_first_class_event_family() -> None:
    event_types = {
        parse_event(json.loads(path.read_text())).event_type
        for path in sorted(FIXTURE_DIR.glob("*.json"))
    }
    assert event_types == {
        "execution_span",
        "attempt",
        "tool_call",
        "validation",
        "failure",
        "usage",
        "outcome",
    }


def test_schema_rejects_sensitive_attribute_key() -> None:
    payload = json.loads((FIXTURE_DIR / "cog-compile-span.json").read_text())
    payload["attributes"] = {"api_key": "forbidden"}
    with pytest.raises(JsonSchemaValidationError):
        union_validator().validate(payload)


def test_schema_rejects_numeric_string_for_integer_field() -> None:
    payload = json.loads((FIXTURE_DIR / "goose-tool-call.json").read_text())
    payload["duration_ms"] = "84"
    with pytest.raises(JsonSchemaValidationError):
        union_validator().validate(payload)


@pytest.mark.parametrize(
    "timestamp",
    [
        "2026-08-23 21:00:00Z",
        "2026-08-23T21:00:00.1234567Z",
    ],
)
def test_schema_rejects_noncanonical_timestamp_lexemes(timestamp: str) -> None:
    payload = json.loads((FIXTURE_DIR / "cog-compile-span.json").read_text())
    payload["occurred_at"] = timestamp
    payload["started_at"] = timestamp
    payload["completed_at"] = timestamp
    payload["duration_ms"] = 0
    with pytest.raises(JsonSchemaValidationError):
        union_validator().validate(payload)


@pytest.mark.parametrize(
    "timestamp",
    [
        0,
        1_690_000_000,
        1_690_000_000.5,
        "2026-08-23 21:00:00Z",
        "2026-08-23T21:00:00.1234567Z",
    ],
)
def test_python_parser_rejects_wire_timestamp_coercions(timestamp: object) -> None:
    payload = json.loads((FIXTURE_DIR / "cog-compile-span.json").read_text())
    payload["occurred_at"] = timestamp
    payload["started_at"] = timestamp
    payload["completed_at"] = timestamp
    payload["duration_ms"] = 0
    with pytest.raises(ValueError):
        parse_event(payload)


def test_schema_rejects_duplicate_evidence_refs() -> None:
    payload = json.loads((FIXTURE_DIR / "deploy-outcome.json").read_text())
    payload["evidence_refs"] = [
        payload["evidence_refs"][0],
        copy.deepcopy(payload["evidence_refs"][0]),
    ]
    with pytest.raises(JsonSchemaValidationError):
        union_validator().validate(payload)


def test_schema_validation_outcome_count_relations() -> None:
    schema = load("validation-event.schema.json")
    validator = Draft202012Validator(schema, registry=registry(), format_checker=FormatChecker())
    base = {
        "schema": "l9.observability.validation-event.v1",
        "event_type": "validation",
        "event_id": "evt-v",
        "occurred_at": "2026-08-23T21:00:00Z",
        "trace": {"trace_id": "t", "span_id": "s", "parent_span_id": None},
        "execution": {"component": "c", "operation": "o"},
        "validator": "pytest",
        "outcome": "fail",
        "failure_count": 0,
    }
    with pytest.raises(JsonSchemaValidationError):
        validator.validate(base)
    base["outcome"] = "not_run"
    base["failure_count"] = 1
    with pytest.raises(JsonSchemaValidationError):
        validator.validate(base)
