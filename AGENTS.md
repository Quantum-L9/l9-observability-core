# AGENTS.md — l9-observability-core

## Mission

Maintain the canonical backend-neutral observability domain vocabulary for Quantum-L9.
This repository is a pure Python utility library outside Constellation. It is not a
service, node, collector, exporter, tracing backend, or CI owner.

## Authority

Authority is scoped by concern rather than treated as one flat precedence list:

- `docs/ARCHITECTURE.md`, `docs/DOMAIN_MODEL.md`, `docs/CORRELATION_MODEL.md`, and
  `docs/ATTRIBUTE_POLICY.md` own semantic meaning, ownership, and domain invariants.
- `docs/COMPATIBILITY.md` owns versioning and compatibility policy.
- `docs/ADOPTION_CONTRACT.md` owns adoption-state and readiness-scope semantics.
- `docs/IDENTITY_AND_DEDUPLICATION.md` owns event-content identity vs delivery/logical-deduplication semantics.
- `docs/EVIDENCE_PROVENANCE.md` owns evidence binding vs external-resolution semantics.
- `docs/ADMISSION_VALIDATION.md` owns cross-event validation guidance at consumer/admission boundaries.
- `schemas/v1/*.json` are canonical for published wire names, types, required fields,
  enums, nullability, and structural constraints.
- Python implementation and executable tests must implement and prove those authorities;
  they do not silently redefine them.

If a semantic document and a wire schema appear to conflict, stop and reconcile the
contract deliberately. Do not let implementation behavior, examples, or tests silently
choose a winner or mutate a published wire contract.

## Owns

- canonical observation event families
- trace/span and L9 execution-coordinate semantics
- exact duration and usage semantics
- evidence references
- bounded extension attributes
- deterministic canonical JSON and SHA-256 digests
- cross-event validation helpers

## Never

- configure logging, tracing, metrics, OpenTelemetry, Prometheus, or dashboards
- host HTTP or MCP
- collect, export, queue, persist, retain, or route observations
- own retry, alerting, assurance, promotion, or deployment policy
- become a Constellation node or duplicate Gate/TransportPacket behavior
- add repository-local CI orchestration
- weaken schemas or tests to obtain a green result

## Completion contract

Run `make verify`. The root `Makefile` is the canonical `tools/l9_repo` facade and must
remain byte-identical to `tools/l9_repo/Makefile.template`; product-specific targets live
in `Repo.mk`. If required development tools are unavailable, report the exact blocked
checks rather than claiming success. Runtime/domain correctness must still be proven
with the behavioral, schema, and compile checks.

## Repository verification profile

Ground truth for this section is the current `Makefile` and `pyproject.toml`.

| Surface | Current contract |
|---|---|
| Repository-local CI workflows | None in this repository tree. Organization CI execution remains externally owned; do not invent local workflow behavior. |
| Pre-commit | No `.pre-commit-config.yaml` is present in this repository tree. Do not assume hooks run locally or in CI. |
| Ruff | Python 3.11 target, line length 100, rules `E,F,B,I,UP`, with `E501` ignored. The repository does not currently state why `E501` is ignored; treat the rationale as `Unknown`, not as a documented false positive. |
| mypy | Python 3.11, `strict = true`, `warn_return_any = true`, `warn_unused_configs = true`, package scope `l9_observability_core`. |
| pytest | Test root `tests/`; warnings are errors via `-W error`. |
| Repository-execution contract | `.l9/repo-workflow.json` owns setup/validate/check/test execution; `tools/l9_repo` executes it. |
| Local verification | `make verify` composes canonical `validate`, `check`, and `test` with schema + compile checks from `Repo.mk`. |
| Deterministic subset | `make test`, `make schema-check`, and `make compile-check` remain independently runnable when optional static-analysis tools are unavailable. |

Current repository inventory contains 14 canonical JSON Schemas, 19 `test_*.py` test modules,
and 8 cross-consumer JSON fixtures. Refresh these counts from the tree before changing this
section; never preserve stale numbers merely because they were previously documented.

## Root documentation map

- `AGENTS.md` is the operating instruction surface for coding agents.
- `ARCHITECTURE.md` is a root index into the machine-readable and semantic architecture authorities.
- `INVARIANTS.md` is the root invariant, enforcement, and intentional-exclusion map.
- `CLAUDE.md` is a thin Claude Code load pointer into the repository authorities; it does not duplicate them.
- `docs/ARCHITECTURE.md` owns detailed product architecture and domain boundaries.
- `README.md` is the human-facing product entrypoint.
- `.l9/architecture.yaml` and `.l9/ownership.yaml` carry machine-readable repository role and ownership.
- `.l9/sdk-compatibility.yaml` carries the supported Python/package-manager compatibility contract.
- `.l9/repo-workflow.json` owns the canonical local repository-execution contract; `Makefile` is its generated facade and product targets live in `Repo.mk`.

Repository-doc refresh source: `l9-update-agent-docs` v2.0.2 from
`Quantum-L9/Cursor-Governance@829f45ec0ac8e1250878e4d8e96a0643ae7412c9`.
All counts and tool facts above come from this repository tree.
