# Correlation Model

## Required lineage

Every canonical event has a `trace_id` and `span_id`.

- A root span has `parent_span_id = null`.
- A child span supplies `parent_span_id` when its parent is known.
- A span MUST NOT name itself as its parent.
- Parent and child must share the same `trace_id`.
- The core does not require OpenTelemetry-specific hexadecimal identifier lengths because existing L9 producers use multiple identifier forms. IDs use a conservative portable ASCII token grammar.

The core validates supplied identifiers. It never generates them.

## Execution hierarchy

The execution coordinate hierarchy is intentionally partial:

`program_id -> campaign_id -> task_id -> run_id -> attempt_id`

The core does not require all ancestors to exist. When a producer has the coordinate, it SHOULD include it. Consumers MUST NOT fabricate missing coordinates.

`run_id` identifies the retryable run lineage when retries are modeled with `AttemptEvent`. `attempt_id` changes per attempt while the run-level coordinates remain stable.

Execution coordinates are semantic identities, not opportunistic slots for any locally unique string. A
protocol-specific result-resource ID, cache key, storage-row ID, or local run-store ID MUST NOT be mapped to
`run_id` unless its owning system explicitly defines it as the canonical retryable execution lineage. If
semantic equivalence is unproved, leave the coordinate absent/null.

## Attempts

For an individual `AttemptEvent`:

- attempts are 1-indexed
- attempt 1 MUST NOT have `prior_attempt_id`
- attempt 1 MUST NOT have `retry_reason`
- attempt N > 1 MUST have `prior_attempt_id`
- an attempt MUST NOT reference itself as its prior attempt
- `execution.attempt_id`, when present, MUST equal the event's `attempt_id`

For `validate_attempt_chain(...)`:

- attempt numbers MUST be contiguous from 1
- attempt IDs MUST be unique
- each retry MUST reference the immediately preceding attempt ID
- all events MUST share one `trace_id`
- stable run coordinates (`component`, `operation`, `program_id`, `campaign_id`, `task_id`, `run_id`) MUST match

The chain helper intentionally does not require `session_id` to remain stable because a retry may cross an interactive/runtime session boundary.

## Causality

Causal event links are explicit event IDs, not inferred from timestamps. A failure event MUST NOT cite itself in `causal_event_refs`. Correlation is not causation.

## Transport independence

Trace context may be carried through HTTP headers, TransportPacket metadata, MCP context, local process context, or another runtime mechanism. This package defines meaning, not carriage.
