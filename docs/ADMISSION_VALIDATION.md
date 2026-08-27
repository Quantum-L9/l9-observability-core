# Admission Validation

## Purpose

The package exposes both per-event validation and cross-event relational validators. Consumers should apply
only the validators whose semantics are owned at their admission boundary.

This document does not turn observations into authoritative world state. It describes validation before a
consumer accepts an observation set under its own policy.

## Validation layers

### 1. Wire and model validation

Use `parse_event()` for untrusted or wire-shaped event data. It rejects unknown schemas, missing wire
discriminators, invalid timestamps, undeclared fields, and model/schema violations.

### 2. Event identity uniqueness

Use `require_unique_event_ids(events)` when a batch/set contract requires every event instance to be unique.
This catches duplicate `event_id` values inside the supplied set. It does not provide distributed exactly-once
semantics.

### 3. Parent/child trace relation

Use `validate_parent_child(parent, child)` when the consumer has an explicitly known parent-child pair. It
requires a shared trace and exact parent-span linkage. Do not infer parenthood from timestamps alone.

### 4. Retry/attempt lineage

Use `validate_attempt_chain(attempts)` when the consumer admits a complete or contractually bounded attempt
chain. It validates contiguous numbering, unique attempt IDs, prior-attempt linkage, stable trace identity,
and stable run-level execution coordinates.

### 5. Producer/domain rules

Apply producer-specific or domain-specific admission rules outside this package. Examples include whether a
particular operation must emit both a failed terminal span and a FailureEvent, whether evidence must be
resolvable, or whether a downstream assurance gate accepts a reported outcome.

### 6. Authoritative state admission

A World Model, assurance system, memory system, accounting plane, or another authoritative consumer decides
whether and how an observation affects its state. Passing this package's validators is necessary evidence of
contract validity, not sufficient authority for a state transition.

## Why there is no generic `validate_all()`

The core deliberately does not compose every validator into one universal admission function. A parent-child
pair, retry chain, unrelated batch, and downstream assurance decision have different ownership and evidence
requirements. A generic composition helper should only be added after multiple real consumers prove the same
admission semantics.
