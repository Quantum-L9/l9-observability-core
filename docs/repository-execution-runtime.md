# Repository Execution Runtime

**Artifact:** `l9-ci-core-repository-execution-runtime`

**Version:** `4.3.1`

This repository vendors the canonical repository-execution runtime under
`tools/l9_repo` from the bound `l9-repo-template` authority. The root `Makefile`
is byte-identical to `tools/l9_repo/Makefile.template` and contains no
product-specific execution logic.

Product-specific utility-library targets live in `Repo.mk`. Organization CI
execution remains owned by `l9-ci-core`; Cursor-Governance remains external and
is accessed only through optional `gov-*` wrappers using `WS=`.

The runtime provenance record `.l9/runtime-provenance.yaml` describes the
vendored `l9-ci-core` repository-execution runtime only. Repo-template birth
commit/tree evidence belongs in handoff evidence, not in that schema.
