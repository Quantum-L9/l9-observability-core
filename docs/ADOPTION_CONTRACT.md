# Adoption Contract

## Purpose

This document defines what it means for an L9 producer or consumer to adopt `l9-observability-core`.
It prevents a validated schema library or helper function from being described as runtime observability
before a real execution path reaches the canonical event boundary.

The core owns event semantics and validation. Producing runtimes own activation. Consumer infrastructure
owns delivery, persistence, indexing, and downstream admission.

## Adoption states

Adoption is progressive. A system MUST NOT claim a later state without evidence for every earlier state.

| State | Meaning | Minimum evidence |
|---|---|---|
| `CONTRACT_ONLY` | The producer understands or references the canonical schemas/models. | Dependency or contract fixture plus schema/model conformance. |
| `PROJECTION_IMPLEMENTED` | Producer-native data can be converted into canonical events. | Pure projection tests using producer semantics. |
| `RUNTIME_REACHABLE` | A real business operation invokes canonical projection on its actual success/failure callgraph. | Integration test through the real operation entrypoint. |
| `HANDOFF_ACTIVE` | Canonical events cross one explicit producer-owned handoff port to an injected next owner. | Spy/contract consumer receives the exact canonical event without changing business semantics. |
| `DURABLE_CONSUMPTION_PROVED` | A downstream owner durably accepts the observation and can retrieve or verify it according to its own contract. | Admission/delivery receipt plus retrieval or equivalent durable evidence. |

Fixtures, examples, direct helper tests, local package builds, and schema validation are valuable evidence,
but they do not by themselves prove `RUNTIME_REACHABLE`.

## Readiness scopes

Readiness claims MUST name their scope.

- **Package readiness**: the core package builds, validates, installs, and preserves its contracts.
- **Producer readiness**: a named producer is `RUNTIME_REACHABLE` and has proven context fidelity and failure isolation.
- **Handoff readiness**: a named producer has an active, explicit next-owner port.
- **Pipeline readiness**: a named downstream delivery/admission path is durably proven.

A handoff pack that proves only package and projection behavior MUST NOT be described as runtime
observability ready.

## Producer conformance profile

A producer claiming `RUNTIME_REACHABLE` SHOULD prove all applicable checks below through its actual
business operation, not a helper-only surrogate:

1. **Success reachability**: one real successful operation creates the intended canonical terminal observation.
2. **Failure reachability**: one real failed operation reaches the canonical failure/lifecycle path.
3. **Context fidelity**: known upstream trace and execution coordinates are preserved exactly.
4. **No fabrication**: unavailable upstream coordinates remain absent/null rather than synthesized.
5. **Single observation boundary**: protocol wrappers do not independently duplicate central producer emission.
6. **Non-interference**: projection or handoff failure does not change the successful business result.
7. **Exception preservation**: observation failure during a business failure does not replace the original business exception.
8. **Lifecycle coherence**: the producer documents whether terminal spans cover both success and failure paths.
9. **Dependency activation**: if observability is configured as required, missing required capability fails activation explicitly rather than silently pretending the feature is active.

## Producer handoff port

The producer-side handoff should be a small dependency-injection boundary that accepts canonical events.
The interface belongs to the producer or its runtime chassis. The implementation behind that port may
queue, persist, export, or project events, but those behaviors remain outside this core library.

A producer MUST NOT add backend transport, persistence, retry, acknowledgement, or exporter policy to
`l9-observability-core` merely to make adoption convenient.

## Failure isolation

Producer observability is a side channel unless deployment policy explicitly makes successful activation a
startup requirement. After the business operation has begun, an observation projection/handoff error MUST
NOT silently rewrite the business result or replace the original business exception.

This rule does not require the core to catch producer exceptions. The producer owns the lifecycle boundary.

## Fixture status

Files under `examples/fixtures/` are wire-contract examples. They demonstrate portability and parser/schema
conformance only. They are never evidence that the named component currently emits the event at runtime.
