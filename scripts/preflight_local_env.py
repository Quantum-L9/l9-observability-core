#!/usr/bin/env python3
"""Validate local env keys for the generic museum example."""

from __future__ import annotations

import sys
from pathlib import Path

REQUIRED = ("L9_ENVIRONMENT",)

REPO_ROOT = Path(__file__).resolve().parents[1]


def resolve_under_repo(candidate: str) -> Path:
    """Resolve ``candidate`` and require it to stay inside the repository.

    The path arrives from ``argv``, so without containment a caller could point
    this at any file on the host (``../../etc/shadow``) and have its contents
    parsed and partially echoed back through the error paths below.
    """
    resolved = Path(candidate).resolve()
    try:
        resolved.relative_to(REPO_ROOT)
    except ValueError as error:
        raise ValueError(f"env file must be inside {REPO_ROOT}: {candidate!r}") from error
    return resolved


def parse_env(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        out[key.strip()] = value.strip()
    return out


def main(argv: list[str]) -> int:
    # The default is anchored to the repository, not to the caller's cwd, so it
    # resolves to the same file however the script is invoked -- and so it cannot
    # fail containment against REPO_ROOT simply because someone ran it from a
    # subdirectory.
    default = str(REPO_ROOT / ".env.example")
    try:
        path = resolve_under_repo(argv[1] if len(argv) > 1 else default)
    except ValueError as error:
        print(str(error), file=sys.stderr)
        return 2
    if not path.is_file():
        print(f"missing env file: {path}", file=sys.stderr)
        return 1
    env = parse_env(path)
    missing = [k for k in REQUIRED if not env.get(k)]
    if missing:
        print(f"missing required keys: {', '.join(missing)}", file=sys.stderr)
        return 1
    if env.get("L9_ENVIRONMENT") not in {"local", "dev", "test", "staging", "prod"}:
        print("L9_ENVIRONMENT must be local|dev|test|staging|prod", file=sys.stderr)
        return 1
    print(f"preflight OK: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
