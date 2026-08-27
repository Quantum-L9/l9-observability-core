"""Repository-execution facade tests for the utility-library materialization."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def _make(*args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    merged = os.environ.copy()
    if env:
        merged.update(env)
    return subprocess.run(
        ["make", "-C", str(REPO), *args],
        check=False,
        capture_output=True,
        text=True,
        env=merged,
    )


def test_makefile_matches_template() -> None:
    assert (REPO / "Makefile").read_bytes() == (
        REPO / "tools" / "l9_repo" / "Makefile.template"
    ).read_bytes()


def test_help_lists_product_and_facade() -> None:
    proc = _make("help")
    assert proc.returncode == 0, proc.stderr
    for token in ("verify", "hygiene-check", "pr-check", "gov-pr-check", "agent-check"):
        assert token in proc.stdout


def test_repo_mk_gov_wrappers_use_ws() -> None:
    text = (REPO / "Repo.mk").read_text(encoding="utf-8")
    assert 'WS="$(CURDIR)"' in text
    for target in ("gov-pr-check", "gov-pr", "gov-start", "gov-wiring-check"):
        assert f"{target}:" in text
    assert "OPEN_PR ?= 0" in text


def test_gov_wrapper_skips_when_gov_root_missing() -> None:
    missing = REPO / ".gov-root-missing-for-test"
    proc = _make("gov-pr-check", env={"GOV_ROOT": str(missing)})
    assert proc.returncode == 0, proc.stderr
    assert "gov: skip" in proc.stdout or "gov: skip" in proc.stderr


def test_utility_repo_mk_has_no_service_demo_targets() -> None:
    text = (REPO / "Repo.mk").read_text(encoding="utf-8")
    for target in ("run:", "dev:", "obs-up:", "obs-down:", "wait-http:"):
        assert f"\n{target}" not in "\n" + text


def test_inventory_check_target() -> None:
    proc = _make("inventory-check")
    if (REPO / "uv.lock").is_file():
        assert proc.returncode == 0, proc.stderr + proc.stdout
    else:
        assert proc.returncode != 0
        assert "missing required file: uv.lock" in proc.stderr + proc.stdout
