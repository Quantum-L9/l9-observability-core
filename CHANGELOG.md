# Changelog

## Unreleased

- Added explicit adoption/readiness states so package/helper validation cannot be misreported as runtime integration.
- Strengthened producer lifecycle/handoff law while keeping transport and persistence outside the core.
- Clarified that `event_digest()` is exact canonical event-content identity, not logical idempotency or exactly-once delivery.
- Added evidence binding vs durable resolution/verification semantics.
- Added consumer-side admission guidance for existing cross-event validators without creating a universal `validate_all()`.
- Expanded the fixture corpus to cover all seven first-class event families while explicitly keeping fixtures non-adoption evidence.
- Prohibited promotion of unrelated protocol/resource identifiers into canonical execution coordinates without proven semantic authority.
- Preserved all v1 schemas and Python domain implementation byte-for-byte.

## 1.0.0 — 2026-08-23

- Established canonical backend-neutral L9 observability domain contracts.
- Added versioned Draft 2020-12 JSON Schemas for seven first-class event families.
- Added strict immutable Pydantic models, exact time/usage semantics, evidence references,
  bounded attributes, deterministic canonical JSON, and semantic event digests.
- Added cross-event correlation and attempt-chain validation.
- Added Cog, Ops, Goose, Program Execution, and Deploy contract fixtures.
- Bound the Cog fixture to canonical RuntimeBundle evidence digests and removed backend-specific adapter leakage.
- Kept the public package compatible with Python 3.11+ while retaining Python 3.12 as the template-pinned development interpreter.
- Hardened JSON safe-integer, digest, causation, retry, validation-count, and mutation rules.
- Materialized as a pure Python library using the l9-repo-template 2.0.0 repository class,
  excluding service/runtime/observability demo surfaces that do not belong to this product.

- PEP 561 `py.typed` marker for downstream strict typing.
- Corrected elapsed-time computation across timezone/DST offset transitions by comparing and subtracting in UTC.
- Tightened wire timestamp parsing to RFC 3339 with explicit timezone and at most microsecond precision, rejecting numeric epoch coercion and lossy higher-precision strings.
- Revalidated observation objects through the registered canonical model before semantic digesting, closing claimed-schema subclass bypasses.
- Required explicit `CostUsage.currency`, matching the published JSON Schema.
- Made bounded attribute iteration deterministic and repaired deep model-copy behavior for immutable mappings.
- Rejected binary-to-text Pydantic coercion at the shared model boundary.
- Rejected unordered or one-shot producer inputs for ordered event-reference collections, preventing hash-seed-dependent event digests.

- Restored the canonical `l9-repo-template` repository-execution chassis: exact Makefile facade,
  `tools/l9_repo`, repository workflow contract/schema, runtime requirements, and product `Repo.mk`.
  This is repository-birth infrastructure only; the public v1 observability contract is unchanged.
- Restored `l9.runtime-provenance/v1` to its canonical `l9-ci-core` runtime-harvest meaning and
  moved repo-template commit/tree identity to handoff evidence rather than repurposing the schema.
