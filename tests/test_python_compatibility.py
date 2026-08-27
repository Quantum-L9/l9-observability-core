"""Syntax-level compatibility guard for the declared Python floor."""

from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_package_syntax_is_python_311_compatible() -> None:
    for path in sorted((ROOT / "src").rglob("*.py")):
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path), feature_version=(3, 11))
