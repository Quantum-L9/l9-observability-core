#!/usr/bin/env python3
"""Rename l9_example_pkg identity to a consumer package name.

With --org/--repo, also rewrites the authoritative repository identity
fields in the .l9 metadata files. Template provenance references (for
example scripts/birth-runner/config.template.yaml template_repo) are
deliberately preserved — provenance is not active repository identity.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

SNAKE_RE = re.compile(r"^[a-z][a-z0-9_]*$")
ORG_RE = re.compile(r"^[A-Za-z0-9]([A-Za-z0-9-]*[A-Za-z0-9])?$")
REPO_RE = re.compile(r"^[A-Za-z0-9._-]+$")
TEMPLATE_IDENTITY = "Quantum-L9/l9-repo-template"
# `repository:` at column 0, and the same key nested one level under `metadata:`.
_REPO_LINE = rf"^repository: {re.escape(TEMPLATE_IDENTITY)}$"
_REPO_LINE_INDENTED = rf"^  repository: {re.escape(TEMPLATE_IDENTITY)}$"
IDENTITY_FILES = (
    (".l9/architecture.yaml", _REPO_LINE_INDENTED),
    (".l9/ownership.yaml", _REPO_LINE),
    (".l9/sdk-compatibility.yaml", _REPO_LINE),
    (".l9/org-birth-profile.yaml", _REPO_LINE),
)
SKIP_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".mypy_cache",
    ".ruff_cache",
    ".pytest_cache",
    ".eggs",
}
SKIP_SUFFIXES = (".egg-info",)
# Files where `l9_example_pkg` is the TEMPLATE SENTINEL, not this repository's
# package identity. Rewriting the sentinel breaks the tool that reads it: a
# renamed `new_repo.py` would reject the very package name it was just given,
# and the rename self-test would assert against its own output.
SKIP_REL_PATHS = {
    "tests/unit/test_bootstrap_rename.py",
    "tests/unit/test_new_repo_orchestrator.py",
    "tests/integration/test_new_repo_local_birth.py",
    "scripts/bootstrap_rename.py",
    "scripts/birth-runner/new_repo.py",
    "scripts/render_cursor_rules.py",
    "MANIFEST.sha256",
    "docs/repository-execution-runtime.md",
}


REPO_ROOT = Path(__file__).resolve().parents[1]


def resolve_within(root: Path, candidate: Path) -> Path:
    """Return ``candidate`` resolved, having proved it stays under ``root``.

    Second line of defence now that ``root`` is anchored to ``__file__``: a
    symlink inside the checkout is still an escape ``rglob`` does not prevent.
    ``Path.rglob`` will not recurse *into* a symlinked directory, but it does
    yield a symlinked file, and ``write_text`` follows it — so a link pointing
    outside the tree would be overwritten in place. Re-resolving at the sink
    refuses that.
    """
    resolved = candidate.resolve()
    try:
        resolved.relative_to(root)
    except ValueError as error:
        raise SystemExit(f"refusing to write outside {root}: {candidate}") from error
    return resolved


def snake_to_kebab(name: str) -> str:
    return name.replace("_", "-")


def replace_text(content: str, snake: str, kebab: str) -> str:
    content = content.replace("l9_example_pkg", snake)
    content = content.replace("l9-example-pkg", kebab)
    return content


def rewrite_repository_identity(root: Path, org: str, repo: str, *, dry_run: bool) -> None:
    """Rewrite authoritative repository identity; never touch provenance refs."""
    identity = f"{org}/{repo}"
    for rel, pattern in IDENTITY_FILES:
        path = root / rel
        if not path.is_file():
            continue
        lines = path.read_text(encoding="utf-8").splitlines()
        updated = False
        for index, line in enumerate(lines):
            if re.match(pattern, line):
                lines[index] = re.sub(r"Quantum-L9/l9-repo-template$", identity, line)
                updated = True
        if updated:
            if not dry_run:
                path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            print(f"identity {rel}: -> {identity}")
        else:
            print(f"identity {rel}: template identity line not present; left unchanged")


def iter_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if any(part.endswith(SKIP_SUFFIXES) for part in path.parts):
            continue
        rel = path.relative_to(root).as_posix()
        if rel in SKIP_REL_PATHS:
            continue
        if rel.startswith("tools/"):
            continue
        # Regenerated via make render-rules after rename.
        if rel.startswith(".cursor/rules/") and rel.endswith(".mdc") and "/templates/" not in rel:
            continue
        if rel == ".cursor/rules/.render-manifest.json":
            continue
        files.append(path)
    return files


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pkg", required=True, help="snake_case package name")
    parser.add_argument("--org", default=None, help="GitHub org for repository identity")
    parser.add_argument("--repo", default=None, help="GitHub repo name for repository identity")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--root", type=Path, default=None)
    args = parser.parse_args(argv)

    snake = args.pkg.strip()
    if not SNAKE_RE.match(snake):
        print(f"invalid --pkg {snake!r}: expect snake_case", file=sys.stderr)
        return 2
    org = (args.org or "").strip()
    repo = (args.repo or "").strip()
    if bool(org) != bool(repo):
        print("--org and --repo must be provided together", file=sys.stderr)
        return 2
    if org and not ORG_RE.match(org):
        print(f"invalid --org {org!r}", file=sys.stderr)
        return 2
    if repo and not REPO_RE.match(repo):
        print(f"invalid --repo {repo!r}", file=sys.stderr)
        return 2
    if snake == "l9_example_pkg":
        print("nothing to do: already l9_example_pkg")
        return 0

    kebab = snake_to_kebab(snake)
    # The tree this rewrites is always the checkout this script lives in, derived
    # from __file__ rather than from argv. --root is kept as an assertion, not as
    # a target: it must name this same repository or the run is refused.
    #
    # The previous form took the root from --root and fell back to __file__. That
    # let a caller point a bulk in-place rewriter at any directory on the host,
    # and it is why the write below was a genuine path-injection sink -- the
    # files read, transformed and written back all derived from an argv value.
    # No caller passes --root: scripts/birth-runner/new_repo.py invokes this with
    # cwd set to the new checkout and no --root at all, relying on exactly this
    # __file__ resolution.
    root = REPO_ROOT
    if args.root is not None and args.root.resolve() != root:
        print(
            f"--root must name this repository ({root}), not {args.root.resolve()}",
            file=sys.stderr,
        )
        return 2
    src_old = root / "src" / "l9_example_pkg"
    src_new = root / "src" / snake
    if not src_old.is_dir():
        print(f"missing source package dir: {src_old}", file=sys.stderr)
        return 1
    if src_new.exists():
        print(f"target package already exists: {src_new}", file=sys.stderr)
        return 1

    planned: list[str] = []
    for path in iter_files(root):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        updated = replace_text(text, snake, kebab)
        if updated != text:
            target = resolve_within(root, path)
            planned.append(str(target.relative_to(root)))
            if not args.dry_run:
                target.write_text(updated, encoding="utf-8")

    planned.append(f"rename src/l9_example_pkg -> src/{snake}")
    if args.dry_run:
        print("dry-run rename plan:")
        for item in planned:
            print(f"  {item}")
        return 0

    src_old.rename(src_new)
    print(f"renamed to {snake} ({kebab})")
    for item in planned:
        print(f"  {item}")
    if org and repo:
        rewrite_repository_identity(root, org, repo, dry_run=args.dry_run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
