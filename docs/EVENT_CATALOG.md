# Event Catalog

All v1 events use JSON Schema draft 2020-12 and reject unknown top-level fields.

| Instance schema | Event type | Purpose |
|---|---|---|
| `l9.observability.execution-span.v1` | `execution_span` | terminal correlated execution unit |
| `l9.observability.attempt-event.v1` | `attempt` | attempt/retry observation |
| `l9.observability.tool-call-event.v1` | `tool_call` | bounded tool invocation |
| `l9.observability.validation-event.v1` | `validation` | validation/check result |
| `l9.observability.failure-event.v1` | `failure` | structured failure classification |
| `l9.observability.usage-event.v1` | `usage` | model/token/cost usage |
| `l9.observability.outcome-event.v1` | `outcome` | declared result/effect observation |

JSON Schema documents use `urn:quantum-l9:observability:v1:*` identifiers. Those URNs identify schema documents without implying a resolvable network endpoint.

## Shared event fields

- `schema`: event-specific instance schema ID
- `event_type`: stable discriminator
- `event_id`: producer-supplied identifier
- `occurred_at`: timezone-aware RFC 3339 timestamp; wire strings require an explicit timezone and at most six fractional digits
- `trace`: `TraceContext`
- `execution`: `ExecutionContext`
- `evidence_refs`: optional array, default empty
- `attributes`: optional bounded immutable scalar map, default empty

## Event-specific requirements

### execution_span

Required: `started_at`, `completed_at`, `duration_ms`, `span_kind`, `status`.

`duration_ms` is the floor of elapsed microseconds divided by 1000.

### attempt

Required: `attempt_id`, `attempt_number`, `status`. Retry attempts (`attempt_number > 1`) require `prior_attempt_id`. Attempt 1 forbids both prior attempt and retry reason. An attempt cannot cite itself as prior.

### tool_call

Required: `tool`, `action`, `outcome`, `duration_ms`.

### validation

Required: `validator`, `outcome`, `failure_count`. `pass` and `not_run` require zero failures; `fail` requires at least one.

### failure

Required: `failure_class`, `failure_code`, `retryable`. `message` is bounded and optional. `causal_event_refs` cannot contain the failure event's own `event_id`.

### usage

Required: `provider`, `model`, `tokens`. `cost` is optional. When `cost` is present, both `currency` and integer `amount_microunits` are required; no default currency is assumed. Supplementary token counters are nullable so unknown is not silently converted to zero.

### outcome

Required: `outcome_kind`, `success`, `effectiveness_signal`. `result_ref` is optional.

## Relational invariants

JSON Schema cannot express every cross-field relationship. Schemas that need such rules include an `x-l9-invariants` annotation. The Python implementation and tests MUST enforce those annotations.

## Compatibility rule

Consumers MUST dispatch by `schema`, not by guessing from field presence. Unknown schema identifiers fail closed in the canonical registry.
