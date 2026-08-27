# Identity and Deduplication

## Event instance identity

`event_id` identifies one producer-created event instance. The producer owns creation and uniqueness policy.
The core validates identifier shape but does not generate IDs or provide a global ID service.

## Canonical content identity

`event_digest(event)` is the SHA-256 digest of the fully normalized canonical event. It is appropriate for:

- exact replay integrity
- exact duplicate-delivery comparison when the same event is resent
- immutable references to one canonical event payload
- regression comparison of canonical event content

The digest covers normalized event state, including producer event identity and timestamps. Two separately
created observations of the same logical operation may therefore have different event digests.

## What `event_digest()` is not

`event_digest()` is not:

- an exactly-once delivery guarantee
- a logical-operation idempotency key
- a retry/run identity
- an ordering or sequence number
- a durable-storage receipt
- a substitute for `event_id`

A downstream delivery/admission system that needs logical deduplication must define its policy using the
producer-owned identities and coordinates appropriate to that boundary. It must not redefine the meaning of
`event_digest()`.

## Correlation identities are not dedupe identities

- `trace_id` groups related correlated work.
- `span_id` identifies one correlated unit.
- `run_id` identifies one retryable run lineage when that semantic is known.
- `attempt_id` identifies one attempt inside a run lineage.

None of those fields should be opportunistically populated from an unrelated local resource ID merely
because the string is unique.

## Replay and delivery

If the exact same canonical event is delivered multiple times, a consumer may compare `event_id` and/or
`event_digest()` according to its delivery contract. Delivery acknowledgements, sequence numbers,
transactionality, and retry policy remain external infrastructure concerns.
