#!/usr/bin/env python3
"""Fail closed when the l9-observability-core repository shell drifts."""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("L9_INVENTORY_ROOT") or Path(__file__).resolve().parents[1])

DENY_DIRS = (
    "engine",
    "chassis",
    "domains",
    "client",
    "database",
    "deploy",
    "example_service",
    "observability",
)
DENY_FILES = (
    "Justfile",
    "justfile",
    "nodespec.yaml",
    "spec.yaml",
    "Dockerfile",
    "docker-compose.yml",
)
DENY_CI_DISTRIBUTION = (
    ".l9/ci-pin",
    "scripts/sync_ci_from_pack.py",
    "requirements-consumer-ci.txt",
    ".github/workflows/l9-analysis.yml",
    ".github/workflows/l9-lint-test.yml",
    ".github/workflows/on-org-update.yml",
    ".github/workflows/governance.yml",
    ".github/governance",
)
TOOLS_ALLOW = frozenset({"l9_repo", "check_workflow_integrity.py"})

REQUIRED = (
    ".l9/runtime-provenance.yaml",
    ".l9/repo-workflow.json",
    ".l9/repo-workflow.schema.json",
    ".l9/architecture.yaml",
    ".l9/ownership.yaml",
    ".l9/sdk-compatibility.yaml",
    ".l9-template-version",
    ".python-version",
    "pyproject.toml",
    "uv.lock",
    "Makefile",
    "Repo.mk",
    "MANIFEST.sha256",
    "requirements-repo-runtime.txt",
    "README.md",
    "AGENTS.md",
    "ARCHITECTURE.md",
    "RUNBOOK.md",
    "VALIDATION.md",
    "docs/repository-execution-runtime.md",
    "src/l9_observability_core/__init__.py",
    "src/l9_observability_core/py.typed",
    "scripts/inventory_check.py",
    "scripts/repo_hygiene_audit.py",
    "scripts/regenerate_runtime_manifest.py",
    "tools/l9_repo/Makefile.template",
    "tools/l9_repo/__init__.py",
    "tools/l9_repo/__main__.py",
    "tools/l9_repo/authority.py",
    "tools/l9_repo/change_policy.py",
    "tools/l9_repo/contract_wiring.py",
    "tools/l9_repo/locking.py",
    "tools/l9_repo/push_preflight.py",
    "tools/l9_repo/reporting.py",
    "tools/check_workflow_integrity.py",
    "tests/unit/test_makefile_targets.py",
)

MENTION_CHECKS = (
    ("AGENTS.md", (".l9/architecture.yaml", ".l9/ownership.yaml", ".l9/sdk-compatibility.yaml")),
    ("ARCHITECTURE.md", ("docs/ARCHITECTURE.md", ".l9/repo-workflow.json")),
)


def main() -> int:
    errors: list[str] = []
    for name in DENY_DIRS:
        if (ROOT / name).exists():
            errors.append(f"deny directory present: {name}/")
    for name in DENY_FILES:
        if (ROOT / name).exists():
            errors.append(f"deny file present: {name}")
    for name in DENY_CI_DISTRIBUTION:
        if (ROOT / name).exists():
            errors.append(
                f"organization CI distribution surface present: {name} - "
                "CI execution/control remains externally owned"
            )

    tools = ROOT / "tools"
    if not tools.is_dir():
        errors.append("tools/ must exist and contain only repository-execution runtime surfaces")
    else:
        for child in sorted(tools.iterdir()):
            if child.name in {"__pycache__", ".DS_Store"}:
                continue
            if child.name not in TOOLS_ALLOW:
                errors.append(f"deny tools entry: tools/{child.name}")

    for rel in REQUIRED:
        if not (ROOT / rel).is_file():
            errors.append(f"missing required file: {rel}")

    pyproject_path = ROOT / "pyproject.toml"
    if pyproject_path.is_file():
        pyproject = pyproject_path.read_text(encoding="utf-8")
        if "constellation-node-sdk" in pyproject:
            errors.append("pyproject.toml must not require constellation-node-sdk")
    for path in (ROOT / "src").rglob("*.py"):
        text = path.read_text(encoding="utf-8", errors="replace")
        if "create_node_app" in text or "register_handler" in text:
            errors.append(
                f"Constellation node API in {path.relative_to(ROOT)} - use L9-Node-Template"
            )

    provenance = ROOT / ".l9" / "runtime-provenance.yaml"
    if provenance.is_file():
        text = provenance.read_text(encoding="utf-8")
        if "l9_ci_core_harvest_revision" not in text:
            errors.append(".l9/runtime-provenance.yaml missing l9_ci_core_harvest_revision")
        if "repo_template:" in text or "tree_sha:" in text:
            errors.append(
                "runtime provenance must not be repurposed as repo-template birth provenance"
            )

    repo_mk = ROOT / "Repo.mk"
    if repo_mk.is_file() and "\nci:" not in "\n" + repo_mk.read_text(encoding="utf-8"):
        errors.append("Repo.mk must define a ci target")

    makefile = ROOT / "Makefile"
    template = ROOT / "tools" / "l9_repo" / "Makefile.template"
    if makefile.is_file() and template.is_file() and makefile.read_bytes() != template.read_bytes():
        errors.append("Makefile must be byte-identical to tools/l9_repo/Makefile.template")

    for rel, needles in MENTION_CHECKS:
        path = ROOT / rel
        if not path.is_file():
            continue
        content = path.read_text(encoding="utf-8")
        for needle in needles:
            if needle not in content:
                errors.append(f"{rel} must mention {needle!r}")

    if errors:
        for err in errors:
            print(f"inventory-check FAIL: {err}", file=sys.stderr)
        return 1
    print("inventory-check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
