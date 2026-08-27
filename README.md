# l9-observability-core

Canonical, backend-neutral observability domain contracts for Quantum-L9.

`l9-observability-core` defines the semantic language used to describe execution observations across L9. It does not collect, export, store, route, display, or alert on telemetry. Producers create typed observations; infrastructure projects those observations into logs, metrics, traces, stores, dashboards, or learning systems.

## Owns

- trace/span correlation semantics
- L9 execution coordinates (`program_id`, `campaign_id`, `task_id`, `run_id`, `attempt_id`)
- canonical event families for execution, attempts, tools, validation, failure, model usage, and outcomes
- evidence references and bounded immutable attributes
- timing and cross-event invariants
- canonical JSON and SHA-256 digests
- deterministic event registry/parsing
- versioned JSON Schemas

## Does not own

- OpenTelemetry setup or exporters
- logging configuration or handlers
- Prometheus/Grafana/Tempo/Loki
- MCP/HTTP servers
- queues, databases, collectors, or background workers
- trace-ID generation middleware
- alerting, anomaly detection, retry policy, assurance decisions, or remediation
- CI or deployment behavior

## Design law

**Observability core models observations; infrastructure transports and projects them.**

A consumer may project one canonical event into OpenTelemetry, JSONL, Prometheus, Graphiti experience memory, a World Model event, or another evidence plane without changing the meaning of the source observation.

## Determinism law

Canonical observations are designed for cross-runtime replay and evidence binding:

- JSON object keys are strings and are serialized in sorted order.
- Canonical integers stay inside the interoperable JSON safe-integer range.
- Floats are forbidden from canonical payloads.
- Canonical timestamps are normalized to UTC with six fractional digits and a `Z` suffix.
- Wire timestamp strings must be RFC 3339, carry an explicit timezone, and use no more than six fractional digits so no producer precision is silently discarded.
- Duration milliseconds are derived with exact integer arithmetic and floor sub-millisecond remainder.
- Canonical SHA-256 digests are rendered as `sha256:<64 lowercase hex>`.
- Mutable producer inputs are copied into immutable model state before they can affect a digest.
- Binary values are rejected rather than silently decoded into text.
- Ordered reference collections reject sets and one-shot iterators so producer container choice cannot perturb event bytes.

## Build order

1. Docs define law and vocabulary.
2. `schemas/v1/` freezes the wire contract.
3. `src/l9_observability_core/` implements that contract.
4. `tests/` proves parity, determinism, and invariants.
5. Consumer fixtures prove wire portability without importing consumer repos. Fixtures are not runtime-adoption evidence.
6. Repository execution is materialized from `Quantum-L9/l9-repo-template` 2.0.0: the canonical local execution chassis is preserved while service/demo surfaces are excluded.

See `docs/ARCHITECTURE.md` and `docs/DOMAIN_MODEL.md` first. Adoption and downstream boundary law is split deliberately:

- `docs/ADOPTION_CONTRACT.md` — runtime reachability/readiness states and producer conformance
- `docs/IDENTITY_AND_DEDUPLICATION.md` — event identity vs delivery/logical deduplication
- `docs/EVIDENCE_PROVENANCE.md` — evidence binding vs external resolution
- `docs/ADMISSION_VALIDATION.md` — cross-event validation at consumer/admission boundaries

## Repository documentation

- `AGENTS.md` — coding-agent operating instructions and verified local-tooling profile
- `ARCHITECTURE.md` — root architecture index and authority map
- `INVARIANTS.md` — repository invariants, enforcement map, and intentional exclusions
- `CLAUDE.md` — thin Claude Code load pointer into the authoritative repo docs
- `docs/ARCHITECTURE.md` — detailed semantic architecture and ownership boundaries
- `RUNBOOK.md` — local build and validation commands
- `VALIDATION.md` — executed validation evidence and remaining external gates


## Install and use

Python 3.11+ is supported. Python 3.12 remains the template-pinned development interpreter.

```bash
python -m pip install -e .
```

```python
from l9_observability_core import parse_event, event_digest

event = parse_event(wire_payload)
digest = event_digest(event)
```

`parse_event()` is fail-closed at the wire boundary: `schema` and `event_type` must be
explicitly present, and timestamps are not accepted through numeric Unix-time coercion
or non-RFC-3339 string forms.

Use `event_digest()` for exact canonical event-content identity because it validates the event and
materializes canonical defaults before hashing. It is not a logical-operation idempotency key or an
exactly-once delivery guarantee. `sha256_digest()` is the lower-level syntactic helper for
already-normalized canonical objects. See `docs/IDENTITY_AND_DEDUPLICATION.md`.

The authoritative cross-runtime wire schemas remain in `schemas/v1/`. Built wheels
also carry those exact files under `share/l9-observability-core/schemas/v1` without a
second generated schema source.
