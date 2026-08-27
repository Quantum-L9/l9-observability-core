# Validation

## Validation contract

The repository uses the canonical local repository-execution chassis from the bound
`l9-repo-template` revision. `.l9/repo-workflow.json` owns setup/validate/check/test execution,
`tools/l9_repo` executes it, the root `Makefile` is its exact facade, and product-specific checks
live in `Repo.mk`. This is local repository verification, not organization CI orchestration.

## Repaired shell state

- template version: `2.0.0`
- template commit and Git tree: recorded in pack-root `evidence/template_materialization.json`
- root Makefile: exact template facade
- canonical `tools/l9_repo/`: present
- `.l9/repo-workflow.json` + schema: present and structurally valid
- `.l9/runtime-provenance.yaml`: canonical `l9-ci-core` runtime-harvest meaning restored
- `.l9/sdk-compatibility.yaml`: utility-library compatibility contract, Python `>=3.11`
- product targets: `Repo.mk`
- FastAPI/Docker/local-observability demo runtime: not materialized
- repository-local organization CI distribution: not materialized

## Executed local proof

| Check | Status | Result |
|---|---|---|
| Domain contract byte comparison | PASS | 38/38 schema/source contract files unchanged from repaired input baseline |
| Prior semantic baseline tests | PASS | 68/68 before adoption-only test expansion |
| Full current repository tests | PASS | 75/75 |
| Schema/fixture suite | PASS | 16/16 |
| Canonical schemas | PASS | 14 |
| Cross-consumer wire fixtures | PASS | 8 fixtures covering all 7 first-class families |
| Event families | PASS | 7 |
| Workflow structural validation | PASS | canonical repo-workflow schema + authority/facade validation |
| Workflow-integrity probe | PASS | facade and required execution surfaces present |
| Source hygiene | PASS | utility-library source/scaffold audit |
| Python compilation | PASS | source/tests/tools/scripts |
| Rebuilt wheel import | PASS | version 1.0.0; 7 event families |
| Rebuilt wheel tests | PASS | 75/75 |
| Rebuilt sdist tests | PASS | 75/75 |

## Next-level adoption hardening

The August 25 executive-architect microscope audit accepted the v1 semantic kernel and identified adoption/readiness ambiguity as the highest-value core improvement. The current tree therefore adds adoption-state law, evidence-resolution boundaries, identity/deduplication semantics, consumer admission guidance, and full seven-family fixture coverage without changing any v1 Python domain source or JSON Schema.

- protected semantic kernel: **38/38 files byte-identical** to the polished baseline
- package source tests: **75/75 PASS**
- schema/fixture tests: **16/16 PASS**
- canonical event families represented by fixtures: **7/7**
- canonical adapter projection tests in the handoff: **12/12 PASS** against source and installed wheel

Package readiness and producer/runtime readiness are now explicitly separate. See `docs/ADOPTION_CONTRACT.md`.

## External blockers

The following are not represented as PASS:

- `uv.lock`: registry/DNS access unavailable; no lockfile was fabricated
- Ruff: module unavailable and cannot be fetched in this runtime
- strict mypy: module unavailable and cannot be fetched in this runtime
- `make validate`, `make verify`, and local-only `make pr-check`: blocked by the required lock/tooling chain
- final repository license: organization authority required

The current Cog remote observation is deliberately not copied into this durable repository document.
See pack-root `evidence/current/cog_runtime_branch.json` and `evidence/current/adoption_matrix.json`.

## Canonical commands once external tooling is available

```bash
python -m pip install -e '.[dev]'
python -m pip install -r requirements-repo-runtime.txt
uv lock
uv lock --check
make validate
make check
make test
make schema-check
make compile-check
make check-config
make check-rules
make verify
make pr-check
```

Do not weaken a schema, model invariant, repository workflow contract, or test to obtain green
output. Resolve drift at the owning contract and preserve failed/blocked evidence honestly.
