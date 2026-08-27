# Domain Model

## Core concepts

### Observation

A typed statement that something occurred in an execution context. An observation describes facts or declared outcomes; it does not make policy decisions and is not automatically authoritative world state.

### Trace

A correlation lineage across related work. `trace_id` identifies the lineage. `span_id` identifies the current correlated unit. `parent_span_id` is optional for roots and supplied when a parent is known.

The core validates supplied identifiers. It does not generate them.

### Execution coordinates

Execution coordinates locate the observation in L9 work without forcing every producer to participate in every hierarchy.

- `program_id`: program-level execution identity
- `campaign_id`: campaign identity
- `task_id`: bounded work item
- `run_id`: one retryable run lineage
- `attempt_id`: one attempt inside that run lineage
- `session_id`: optional interactive/runtime session
- `component`: producer identity
- `operation`: canonical or producer-owned operation name
- `phase`: optional phase/step identifier

`component` and `operation` are required. Hierarchical IDs are optional because not every L9 subsystem runs inside PE.

### Evidence reference

A pointer to external evidence. The core validates shape and digest syntax but does not dereference, authorize, persist, or prove the evidence itself. SHA-256 digests use the canonical `sha256:<hex>` form.

### Bounded attributes

A narrow immutable extension surface for low-cardinality scalar metadata. Attributes are not a side door for arbitrary JSON.

## Event families

### ExecutionSpan

Describes the terminal state of one execution span with start/end timestamps, exact whole-millisecond duration, span kind, and status.

### AttemptEvent

Describes one bounded attempt and its retry lineage. Attempt numbers start at 1. Retry attempts reference the immediately preceding attempt when validated as a chain.

### ToolCallEvent

Describes a tool invocation without embedding unrestricted inputs or outputs. It records tool, action, outcome, duration, and optional request/result evidence references.

### ValidationEvent

Describes a validator/check result. Outcomes use `pass`, `fail`, `blocked`, `unknown`, or `not_run`.

- `pass` requires `failure_count = 0`
- `fail` requires `failure_count >= 1`
- `not_run` requires `failure_count = 0`

`blocked` and `unknown` may carry a nonzero count when partial execution established failures before the terminal state became blocked or unknown.

### FailureEvent

Describes a structured failure classification, stable code, retryability declaration, causal event references, and an optional bounded sanitized message. It is not a raw exception or stack-trace container.

### UsageEvent

Describes model/provider token and cost usage using exact integers.

`TokenUsage.total_tokens` is the producer/provider's aggregate total. Optional counters such as cache-read, cache-write, and reasoning tokens are supplementary dimensions and are **not assumed additive** because providers account for them differently. `null` means not reported/unknown; `0` means explicitly observed zero.

`CostUsage` carries an explicit three-letter uppercase ASCII currency code plus an integer
microunit amount. There is no implicit default currency.

### OutcomeEvent

Describes a declared result/effect signal without deciding promotion or policy. Numeric effectiveness remains domain-specific unless promoted later; v1 uses a bounded qualitative signal.

## Status vs failure

Status answers **what terminal state the observed operation reached**. Failure events answer **what failed and how it is classified**. A producer that models an operation lifecycle with `ExecutionSpan` SHOULD emit a terminal span for every terminal path, including failure. When a reusable failure classification exists, a failed operation SHOULD additionally emit a separately identified `FailureEvent`. A failure-classification event is not automatically a substitute for lifecycle terminal-state evidence.

## Observation vs authoritative world state

These events report execution observations. They are not, by themselves, authoritative operational truth. A World Model or owning system may admit/project them into authoritative state under its own rules.
