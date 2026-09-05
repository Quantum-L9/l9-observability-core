from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Sequence


class ChangePolicyError(RuntimeError):
    """Raised when changed-file context cannot be resolved safely."""


_GIT_REV_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9._/@^~-]{0,254}")
"""Conservative allowlist for the revisions this module hands to git.

Deliberately narrower than git's own ``check-ref-format``: it admits the
``refs/heads/x``, ``origin/main``, ``HEAD^``, ``v1.2.3`` and abbreviated-SHA
forms callers actually pass, and nothing else."""


def _validate_git_rev(rev: str, label: str) -> str:
    """Return ``rev`` once it is proven to be a plain git revision.

    ``base_ref`` and ``head_ref`` reach this module straight from ``argv`` and
    are then passed to ``git`` as command arguments. The leading-character rule
    is the load-bearing one: a value like ``--upload-pack=…`` is a *valid* string
    to ``subprocess`` but git reads it as an option, which turns a diff into
    arbitrary command execution. ``..`` is rejected because git forbids it in ref
    names and it is how a range expression smuggles in a second revision.
    """
    if not _GIT_REV_PATTERN.fullmatch(rev):
        raise ChangePolicyError(f"{label} is not a valid git revision: {rev!r}")
    if ".." in rev or rev.endswith((".lock", "/", ".")):
        raise ChangePolicyError(f"{label} is not a valid git revision: {rev!r}")
    return rev


@dataclass(frozen=True)
class ChangedFileResolution:
    files: tuple[str, ...]
    source: str
    base_ref: str | None = None
    head_ref: str | None = None


@dataclass(frozen=True)
class SelectedGate:
    gate_id: str
    blocking: bool
    commands: tuple[tuple[str, ...], ...]


@dataclass(frozen=True)
class CompanionFinding:
    rule_id: str
    message: str
    changed: tuple[str, ...]
    required_any: tuple[str, ...]
    missing_all: tuple[str, ...]


def _run_git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            ["git", *args],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )
    except OSError as error:
        raise ChangePolicyError(f"unable to execute git: {error}") from error


def _lines(proc: subprocess.CompletedProcess[str], failure: str) -> list[str]:
    if proc.returncode != 0:
        raise ChangePolicyError(proc.stderr.strip() or failure)
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def _normalize_repo_path(path: str) -> str:
    if not path or "\x00" in path or "\n" in path or "\r" in path:
        raise ChangePolicyError(
            "changed file path must be a non-empty single-line path"
        )
    if "\\" in path:
        raise ChangePolicyError(
            f"changed file path must use POSIX separators: {path!r}"
        )
    candidate = PurePosixPath(path)
    if candidate.is_absolute() or ".." in candidate.parts or path.startswith("./"):
        raise ChangePolicyError(
            f"changed file path is not canonical repository-relative: {path!r}"
        )
    normalized = candidate.as_posix()
    if normalized in {"", "."} or normalized != path:
        raise ChangePolicyError(
            f"changed file path is not canonical repository-relative: {path!r}"
        )
    return normalized


def _normalize_paths(paths: Sequence[str]) -> list[str]:
    return [_normalize_repo_path(path) for path in paths]


def _run_git_paths(root: Path, *args: str) -> list[str]:
    try:
        proc = subprocess.run(
            ["git", "-c", "core.quotePath=false", *args, "-z"],
            cwd=root,
            capture_output=True,
            check=False,
        )
    except OSError as error:
        raise ChangePolicyError(f"unable to execute git: {error}") from error
    if proc.returncode != 0:
        detail = proc.stderr.decode("utf-8", errors="replace").strip()
        raise ChangePolicyError(detail or f"git {' '.join(args)} failed")
    try:
        decoded = proc.stdout.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ChangePolicyError("git returned a non-UTF-8 repository path") from error
    return _normalize_paths([path for path in decoded.split("\0") if path])


def _working_tree_files(root: Path) -> list[str]:
    unstaged = _run_git_paths(root, "diff", "--no-renames", "--name-only", "HEAD")
    staged = _run_git_paths(root, "diff", "--cached", "--no-renames", "--name-only")
    untracked = _run_git_paths(root, "ls-files", "--others", "--exclude-standard")
    return [*unstaged, *staged, *untracked]


def _comparison_files(root: Path, base_ref: str, head_ref: str) -> list[str]:
    base_ref = _validate_git_rev(base_ref, "base ref")
    head_ref = _validate_git_rev(head_ref, "head ref")
    verify = _run_git(root, "rev-parse", "--verify", base_ref)
    if verify.returncode != 0:
        detail = verify.stderr.strip() or "git rev-parse failed"
        raise ChangePolicyError(f"comparison ref is unavailable: {base_ref}: {detail}")
    merge_base = _run_git(root, "merge-base", base_ref, head_ref)
    bases = _lines(
        merge_base,
        f"unable to compute merge-base for {base_ref} and {head_ref}",
    )
    if len(bases) != 1:
        raise ChangePolicyError(
            f"expected one merge-base for {base_ref} and {head_ref}, got {len(bases)}"
        )
    return _run_git_paths(
        root, "diff", "--no-renames", "--name-only", bases[0], head_ref
    )


def resolve_changed_files(
    root: Path,
    *,
    explicit: Sequence[str] = (),
    base_ref: str | None = None,
    head_ref: str = "HEAD",
) -> ChangedFileResolution:
    """Resolve a deterministic change set without silently treating no context as clean.

    Explicit files win. Otherwise committed changes are resolved from the merge-base
    of ``base_ref`` and ``head_ref`` and unioned with staged, unstaged, and untracked
    files. If no comparison ref is available and the working tree is clean, the
    operation fails with ``ChangePolicyError`` rather than returning a false empty set.
    """

    if explicit:
        files = tuple(sorted(dict.fromkeys(_normalize_paths(explicit))))
        return ChangedFileResolution(files=files, source="explicit")

    working = _working_tree_files(root)
    committed: list[str] = []
    source = "working-tree"
    if base_ref:
        try:
            committed = _comparison_files(root, base_ref, head_ref)
            source = "comparison+working-tree" if working else "comparison"
        except ChangePolicyError:
            if not working:
                raise
            source = "working-tree;comparison-unavailable"
    elif not working:
        raise ChangePolicyError(
            "no changed-file context: provide explicit files or a resolvable base ref"
        )

    files = tuple(sorted(dict.fromkeys([*committed, *working])))
    return ChangedFileResolution(
        files=files,
        source=source,
        base_ref=base_ref,
        head_ref=head_ref if base_ref else None,
    )


def changed_files(
    root: Path,
    *,
    base: str | None = None,
    head: str | None = None,
    explicit: Sequence[str] = (),
) -> list[str]:
    """Compatibility wrapper returning only the resolved file list."""

    resolution = resolve_changed_files(
        root,
        explicit=explicit,
        base_ref=base,
        head_ref=head or "HEAD",
    )
    return list(resolution.files)


def _matches(path: str, prefixes: Sequence[str]) -> bool:
    return any(path.startswith(prefix) for prefix in prefixes)


def select_gates(policy: dict[str, Any], files: Sequence[str]) -> list[SelectedGate]:
    selected: list[SelectedGate] = []
    gates = policy["gates"]
    for gate_id in policy["gate_order"]:
        gate = gates[gate_id]
        if any(_matches(path, gate["match_any_prefix"]) for path in files):
            selected.append(
                SelectedGate(
                    gate_id=gate_id,
                    blocking=gate["blocking"],
                    commands=tuple(tuple(command) for command in gate["commands"]),
                )
            )
    return selected


def companion_findings(
    policy: dict[str, Any], files: Sequence[str]
) -> list[CompanionFinding]:
    findings: list[CompanionFinding] = []
    file_set = set(files)
    for rule in policy["companion_rules"]:
        hits = tuple(path for path in files if _matches(path, rule["match_any_prefix"]))
        if not hits:
            continue
        required_any = tuple(rule.get("require_any_prefix", ()))
        missing_any = bool(required_any) and not any(
            _matches(path, required_any) for path in files
        )
        required_all = tuple(rule.get("require_all_paths", ()))
        missing_all = tuple(path for path in required_all if path not in file_set)
        if missing_any or missing_all:
            findings.append(
                CompanionFinding(
                    rule_id=rule["id"],
                    message=rule["message"],
                    changed=hits,
                    required_any=required_any if missing_any else (),
                    missing_all=missing_all,
                )
            )
    return findings
