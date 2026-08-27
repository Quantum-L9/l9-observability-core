#!/usr/bin/env python3
"""Regenerate the complete source-tree MANIFEST.sha256 deterministically."""

from __future__ import annotations

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "MANIFEST.sha256"
EXCLUDED_PARTS = {
    ".git",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "build",
    "dist",
}
EXCLUDED_NAMES = {"MANIFEST.sha256", ".DS_Store"}


def iter_files() -> list[Path]:
    files: list[Path] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.is_symlink():
            continue
        rel = path.relative_to(ROOT)
        if any(part in EXCLUDED_PARTS for part in rel.parts):
            continue
        if rel.name in EXCLUDED_NAMES or rel.suffix == ".pyc":
            continue
        files.append(path)
    return sorted(files, key=lambda item: item.relative_to(ROOT).as_posix())


def main() -> int:
    lines = []
    for path in iter_files():
        rel = path.relative_to(ROOT).as_posix()
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        lines.append(f"{digest}  {rel}")
    MANIFEST.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote MANIFEST.sha256 ({len(lines)} entries)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
