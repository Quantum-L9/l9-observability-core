# Architecture Index — l9-observability-core

This root file is an **index**, not a second architecture specification. Detailed semantics remain
owned by the authorities linked below.

Documentation snapshot: 2026-08-25, refreshed with `l9-update-agent-docs` v2.0.2 from
`Quantum-L9/Cursor-Governance@829f45ec0ac8e1250878e4d8e96a0643ae7412c9`.

## Repository identity

`l9-observability-core` is a reusable, backend-neutral Python utility library outside the
Constellation node runtime. It defines canonical observation contracts and pure validation helpers;
it does not own telemetry transport, storage, exporters, servers, dashboards, CI execution, or
deployment.

## Authority map

| Concern | Authority |
|---|---|
| Repository role and architecture boundary | [`.l9/architecture.yaml`](.l9/architecture.yaml) |
| Repository ownership split | [`.l9/ownership.yaml`](.l9/ownership.yaml) |
| Python/package-manager compatibility | [`.l9/sdk-compatibility.yaml`](.l9/sdk-compatibility.yaml) |
| Local repository-execution contract | [`.l9/repo-workflow.json`](.l9/repo-workflow.json) |
| Detailed semantic architecture | [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) |
| Domain vocabulary | [`docs/DOMAIN_MODEL.md`](docs/DOMAIN_MODEL.md) |
| Correlation and attempt lineage | [`docs/CORRELATION_MODEL.md`](docs/CORRELATION_MODEL.md) |
| Attribute extension policy | [`docs/ATTRIBUTE_POLICY.md`](docs/ATTRIBUTE_POLICY.md) |
| Compatibility and versioning | [`docs/COMPATIBILITY.md`](docs/COMPATIBILITY.md) |
| Consumer boundary | [`docs/INTEGRATION_CONTRACT.md`](docs/INTEGRATION_CONTRACT.md) |
| Adoption/readiness law | [`docs/ADOPTION_CONTRACT.md`](docs/ADOPTION_CONTRACT.md) |
| Event identity/deduplication law | [`docs/IDENTITY_AND_DEDUPLICATION.md`](docs/IDENTITY_AND_DEDUPLICATION.md) |
| Evidence provenance/resolution law | [`docs/EVIDENCE_PROVENANCE.md`](docs/EVIDENCE_PROVENANCE.md) |
| Admission validation law | [`docs/ADMISSION_VALIDATION.md`](docs/ADMISSION_VALIDATION.md) |
| Published wire structure | [`schemas/v1/`](schemas/v1/) |
| Agent operating instructions | [`AGENTS.md`](AGENTS.md) |
| Repository invariants and enforcement | [`INVARIANTS.md`](INVARIANTS.md) |
| Claude Code load pointer | [`CLAUDE.md`](CLAUDE.md) |

If a semantic document and a wire schema appear to conflict, stop and reconcile the owning
contracts. This index does not choose a winner and must not duplicate their contents.

## Package map

```text
schemas/v1/                    canonical JSON Schema wire contracts
src/l9_observability_core/     typed models, canonicalization, registry, validation helpers
tests/                         contract, determinism, regression, and compatibility proof
examples/fixtures/             cross-consumer wire examples
docs/                          semantic law, compatibility, integration, and non-goals
.l9/                           machine-readable repository role, ownership, and provenance
```

Current repository inventory: 14 canonical JSON Schemas, 23 Python source modules, 19
`test_*.py` test modules, and 8 cross-consumer JSON fixtures.

## Verification architecture

The repository intentionally contains no `.github/workflows/` directory and no
`.pre-commit-config.yaml` in this delivered product tree. Local repository execution is owned by
`.l9/repo-workflow.json` and the vendored `tools/l9_repo` runtime. The root `Makefile` is a
generated, byte-stable facade; product-specific targets live in `Repo.mk`. Lint/type/test
configuration remains owned by `pyproject.toml`.

| Check | Source |
|---|---|
| Structural/local execution validation | `make validate`; `.l9/repo-workflow.json` |
| Ruff lint + format | `make check` / `make lint`; `pyproject.toml` |
| Strict mypy | `make check` / `make typecheck`; `pyproject.toml` |
| Behavioral tests | `make test`; pytest config in `pyproject.toml` |
| Schema-focused tests | `make schema-check` |
| Python compilation | `make compile-check` |
| Full local verification | `make verify` |

Repository-local deterministic verification is defined here; organization CI orchestration is not.
`.l9/ownership.yaml` assigns organization CI ownership externally to `Quantum-L9/l9-ci-core` and
the organization control plane.

## Current lint/type facts

- Ruff target: `py311`
- Ruff line length: `100`
- Ruff selected rules: `E`, `F`, `B`, `I`, `UP`
- Ruff ignored rule: `E501`; rationale is not documented in the repository and is therefore `Unknown`
- mypy: Python 3.11 with strict mode, `warn_return_any`, and `warn_unused_configs`
- pytest: `tests/` with warnings treated as errors

For product semantics, continue to [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).
