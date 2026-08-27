# Integration Contract

This document defines producer and consumer responsibilities without coupling the core package to producer
repositories or infrastructure backends.

See also:

- `ADOPTION_CONTRACT.md` for runtime reachability/readiness states and producer conformance
- `EVIDENCE_PROVENANCE.md` for evidence binding and external resolution
- `IDENTITY_AND_DEDUPLICATION.md` for event identity vs delivery/logical deduplication
- `ADMISSION_VALIDATION.md` for cross-event validation at consumer boundaries

## Core ownership boundary

`l9-observability-core` owns canonical event meaning, wire shape, deterministic normalization/digests,
correlation semantics, evidence-reference shape, and pure validation helpers.

The core does not own when an observation exists. The producing runtime owns instrumentation timing and
producer-native semantic projection.

The core does not own the observation's next hop. Transport, buffering, persistence, indexing, delivery
acknowledgement, retry, and durable admission remain external.

## Producer lifecycle contract

A producer integrating this package SHOULD place canonical projection at one central business-operation
boundary rather than duplicating projection in every protocol wrapper.

For a synchronous operation, the healthy shape is:

```text
business operation
  -> producer lifecycle boundary
  -> canonical projection
  -> explicit producer-owned handoff port
  -> externally supplied next owner
```

The producer owns:

- start/terminal timing
- event/span identity according to the producer's actual authority
- propagation of known upstream trace/execution coordinates
- failure classification when a stable reusable mapping exists
- the decision whether terminal span symmetry is required for the operation
- invoking the next-owner port

The producer MUST NOT fabricate upstream program/campaign/task/run/attempt/session coordinates merely to
populate a canonical event.

A local result-resource identifier, cache key, database row ID, or protocol-specific request ID MUST NOT be
mapped into a canonical execution coordinate unless the owning system explicitly declares semantic
equivalence.

## Error isolation

Unless deployment policy makes observability activation a startup requirement, per-operation observation is
a side channel. Projection or handoff failure after a business operation has started MUST NOT silently:

- convert a successful business result into failure
- replace or mask the original business exception
- cause a protocol wrapper to duplicate a central observation

If observability is configured as required, missing required capability SHOULD fail activation/configuration
early and explicitly rather than silently pretending the feature is active.

## Failure lifecycle

`ExecutionSpan` reports lifecycle terminal state. `FailureEvent` reports reusable failure classification.
A producer that uses `ExecutionSpan` to represent an operation lifecycle SHOULD emit a terminal span on both
successful and failed terminal paths. When a stable failure classification exists, it SHOULD additionally
emit a separately identified `FailureEvent` using the same trace/execution context and explicit causality.

The producer owns the exact lifecycle policy. A `FailureEvent` is not automatically a replacement for a
terminal span.

## Producers

### Cognitive runtime

May emit compilation/planning `ExecutionSpan`, `ValidationEvent`, `UsageEvent`, `FailureEvent`, and
`OutcomeEvent` observations. Cognitive logic owns when those observations are created; this package owns
their shape.

### Ops/context plane

May emit context-resolution, kernel-resolution, memory-hydration `ExecutionSpan` and `ValidationEvent`
observations. Context payloads are not embedded in attributes.

### Goose/execution runtimes

May emit agent `ExecutionSpan`, `AttemptEvent`, `ToolCallEvent`, `UsageEvent`, `FailureEvent`, and
`OutcomeEvent` observations. The execution runtime owns actual instrumentation and carriage.

### Program Execution

May bind `program_id`, `campaign_id`, `task_id`, `run_id`, and `attempt_id` coordinates. PE attempt receipts
remain PE-owned artifacts; observability events may reference them as evidence.

### Gate / node runtimes

May propagate trace context and emit execution observations. `TransportPacket` remains the transport
contract; observability events do not replace it.

### Deployment

May emit deployment `ExecutionSpan`, `ValidationEvent`, `FailureEvent`, and `OutcomeEvent` observations.
Deployment receipts remain deployment-owned evidence.

## Consumer rules

Consumers MUST NOT:

- treat `attributes` as an unrestricted payload channel
- treat an observation as an assurance verdict
- treat an `OutcomeEvent` as automatic policy promotion
- assume or fabricate missing execution coordinates
- rewrite producer event IDs or evidence digests
- claim runtime adoption solely because a fixture or helper test passes
- claim durable evidence retrievability solely because an `EvidenceRef.digest` exists

## Projection rule

Adapters may project canonical observations to backend-specific records. Projection-specific fields must not
mutate the canonical source event. Downstream source identifiers, event digests, evidence metadata, and
trace/execution coordinates should remain available for provenance.
