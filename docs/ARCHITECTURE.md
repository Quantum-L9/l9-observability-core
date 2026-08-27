# Architecture

## Identity

`l9-observability-core` is a reusable Python platform library. It is not a Constellation node, service, MCP server, collector, exporter, or observability backend.

## Ownership boundary

| Concern | Owner |
|---|---|
| Canonical observation semantics | `l9-observability-core` |
| Instrumentation points | producing component |
| ID generation | producing component / owning runtime |
| Logger/tracer/metric configuration | consumer chassis/infrastructure |
| Transport/export | consumer infrastructure |
| Persistence/indexing | external backend / owning system |
| Dashboards/alerts | operations layer |
| Retry/remediation/promotion decisions | owning policy system |

The core must remain importable without starting threads, opening sockets, reading environment variables, configuring logging, reading a clock, generating IDs, or contacting a backend.

## Event model

Every first-class event carries:

- an event-specific `schema` identifier
- `event_id`
- `occurred_at`
- `trace` correlation
- `execution` coordinates
- zero or more `evidence_refs`
- bounded immutable scalar `attributes`

Event families add only semantics that deserve cross-L9 meaning.

## Canonicalization

Canonical JSON is UTF-8 JSON with:

- string object keys only
- sorted object keys
- compact separators
- JSON-native scalar values
- integers bounded to `[-9007199254740991, 9007199254740991]`
- floats forbidden
- timezone-aware datetimes normalized to UTC
- timestamps rendered with exactly six fractional digits and `Z`
- binary values are rejected rather than coerced into text
- ordered reference collections accept only list/tuple producer inputs; unordered sets and one-shot iterators are rejected

The SHA-256 digest is computed over those canonical bytes and rendered as `sha256:<64 lowercase hex>`.

Canonical domain payloads avoid floating-point fields for durations and money. Durations are integer milliseconds. Monetary amounts use integer microunits and an explicit uppercase three-letter currency code; the core does not assume a default currency.

Wire timestamp strings use RFC 3339 with an explicit timezone and at most six fractional
digits. Programmatic producers may supply timezone-aware `datetime` objects. Numeric epoch
values and space-separated datetime strings are rejected rather than silently coerced.

## Timing law

For interval-bearing observations:

`duration_ms = floor((completed_at - started_at) / 1 millisecond)`

The implementation uses integer datetime components rather than floating-point seconds. A producer MUST supply the same value or validation fails. Sub-millisecond remainder is intentionally discarded.

Ordering and subtraction are performed after conversion to UTC. This keeps elapsed time
correct across timezone-offset transitions such as daylight-saving folds, where wall-clock
subtraction of two datetimes sharing one `tzinfo` object can otherwise ignore the offset change.

## Immutability law

Canonical event models are frozen and all collection-valued fields are immutable after validation. In particular, producer-provided attribute dictionaries are copied into immutable mappings before the event can be canonicalized or hashed. This prevents a previously computed digest from being invalidated by later mutation through a retained input reference.

## Compatibility

Wire schemas are identified with non-resolving `urn:quantum-l9:observability:v1:*` JSON Schema identifiers. Event instances use stable `l9.observability.*.v1` values in their `schema` field.

A v1 producer MUST NOT add undeclared top-level fields. Breaking semantic or structural changes require v2. See `COMPATIBILITY.md`.

## Adoption and runtime reachability

The core can be fully correct while a producer remains unwired. Package/schema/helper validation therefore
does not prove runtime observability. `ADOPTION_CONTRACT.md` defines progressive adoption states from
`CONTRACT_ONLY` through `DURABLE_CONSUMPTION_PROVED`.

The producer owns the lifecycle point where an observation becomes real. A healthy producer exposes one
central projection/handoff seam and keeps backend transport outside the core.

Readiness claims must name their scope: package readiness, producer readiness, handoff readiness, or
pipeline readiness. A locally replayable package must not be described as a runtime-integrated producer
unless the real business callgraph has been exercised.

## Relationship to existing L9 observability

Existing repositories may have logger, metric, trace, or receipt formats. Those are producer-local projections or legacy contracts. This package is the canonical semantic layer for new shared observation contracts. Adoption is explicit and incremental; it does not silently rewrite historical artifacts.

## Security boundary

Observations are metadata, not arbitrary payload dumps. Tool request/response bodies, credentials, authorization headers, cookies, secret values, prompts containing secrets, and unrestricted exception payloads are outside the canonical event model.

## Non-goals

See `NON_GOALS.md`.
