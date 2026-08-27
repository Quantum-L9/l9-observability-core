# Runbook

## Purpose

Validate and package `l9-observability-core` without starting a service or external
observability backend.

## Setup

Python 3.11 or newer is required. Python 3.12 remains the template-pinned development interpreter.

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[dev]'
```

## Validation

```bash
make test
make schema-check
make compile-check
make lint
make typecheck
# or all of the above
make verify
```

Expected behavior:

- every JSON Schema passes Draft 2020-12 meta-validation
- all 8 fixtures validate through the canonical event union and Python parser, covering all 7 first-class event families
- canonicalization and event digests are deterministic
- negative contract vectors fail closed
- no network, database, collector, exporter, HTTP, MCP, or logging setup is required

## Build

```bash
make build
```

The wheel includes the Python package and the authoritative `schemas/v1/*.json` files
as package data-files under `share/l9-observability-core/schemas/v1`.

## Failure handling

Do not weaken a schema or test to make validation pass. Resolve schema/model/test drift
at the owning contract. If a development tool cannot be installed or executed, report
that check as blocked and run every remaining deterministic check.

## Extension workflow

1. Update semantic law in `docs/`.
2. Update the canonical v1 schema only for compatible changes; otherwise create a new version.
3. Update Python models to implement the schema.
4. Add positive and negative regression tests.
5. Validate cross-consumer fixtures and preserve full seven-family fixture coverage.
6. If producer/consumer integration behavior changes, update `docs/ADOPTION_CONTRACT.md`, `docs/INTEGRATION_CONTRACT.md`, and the relevant identity/evidence/admission guidance without adding backend ownership to the core.
