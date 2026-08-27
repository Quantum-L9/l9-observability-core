# Compatibility Policy

## Python compatibility

The v1 Python package supports Python 3.11 and newer. The repository keeps Python 3.12 as its template-pinned development interpreter, but package source MUST remain syntactically valid for Python 3.11 unless a future major compatibility decision changes that floor.

## Version identity

Wire compatibility is identified by the event-specific instance `schema` value. v1 schema documents live in `schemas/v1/` and use stable `urn:quantum-l9:observability:v1:*` JSON Schema `$id` values.

The URN is an identifier, not a network location. Schema resolution is local/package-controlled and must not require network access.

Wire events must explicitly carry both `schema` and `event_type`. The Python parser may
materialize optional defaults after validation, but it does not synthesize a missing wire
discriminator. Wire timestamp strings are RFC 3339 with explicit timezone and at most six
fractional digits, matching the precision preserved by the canonical representation.

The Python models also preserve the published fail-closed/deterministic contract at the
programmatic boundary: binary values are not decoded into strings, and ordered reference
collections reject unordered sets and one-shot iterators instead of accepting container
coercions that could change canonical bytes across processes.

## Backward-compatible changes

A future v1.x implementation may:

- improve documentation without changing wire meaning
- add parser/helpers that do not change wire semantics
- add a new event schema with a new instance `schema` identifier
- add stricter implementation validation only when it enforces an invariant already published in the v1 contract
- relax an implementation bug when the published JSON Schema and documented contract already allowed the value

## Breaking changes

Require a new major instance schema version:

- adding required fields to an existing event
- changing field meaning
- changing status/failure enum meaning
- changing canonicalization rules
- changing identifier grammar
- changing timing or monetary units
- changing null-vs-zero meaning
- allowing previously forbidden arbitrary payloads

## Unknown fields

All v1 event schemas set `additionalProperties: false`. This is intentional. Extensions use bounded `attributes` or a new versioned schema.

## Unknown schemas

The Python event registry rejects unknown or malformed schema identifiers. Callers must explicitly upgrade before interpreting a new schema.

## Historical artifacts

Legacy L9 telemetry/receipt formats are not retroactively invalidated. Adapters may translate them into this model when semantics are provably equivalent. Translation must preserve provenance and must not fabricate unavailable fields.
