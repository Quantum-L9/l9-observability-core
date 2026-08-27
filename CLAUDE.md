# Claude Code Entry Point - l9-observability-core

This file is a load pointer, not a competing policy or architecture source.

Before changing this repository, read in order:

1. [`AGENTS.md`](AGENTS.md) for operating instructions and authority boundaries.
2. [`ARCHITECTURE.md`](ARCHITECTURE.md) for the repository and package map.
3. [`INVARIANTS.md`](INVARIANTS.md) for enforcement, lint/type facts, and intentional exclusions.
4. [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) plus the relevant domain documents for semantic law.
5. [`schemas/v1/`](schemas/v1/) for the published wire contract.
6. [`RUNBOOK.md`](RUNBOOK.md) and [`VALIDATION.md`](VALIDATION.md) before claiming completion.

Use `make verify` for the full local verification surface. If an external dependency or tool blocks a
required gate, preserve that blocker as evidence rather than weakening the contract.

There is no repository-local `.claude/README.md`, skill registry, or project-specific update-agent-docs
adapter in this tree. Do not fabricate one. Cursor-Governance remains an external control plane and is
invoked only through the existing `make gov-*` wrappers when it is wired in the operator environment.
