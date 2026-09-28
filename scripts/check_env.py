#!/usr/bin/env python3
"""Environment preflight for reqtriage.

Run this before anything else in class: `python scripts/check_env.py`
(no shell script — this must work identically on Windows PowerShell,
WSL, and Linux/macOS bash). It checks the things that actually cause
lost classroom time, and prints a clear PASS/FAIL for each.

Exit code 0 if every check passes, 1 otherwise.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
EXPECTED_PYDANTIC = "2.13.5"
EXPECTED_PYTEST = "9.1.1"

_results: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    _results.append((name, ok, detail))


def main() -> int:
    # --- Python version ---
    py_ok = sys.version_info >= (3, 11)
    check(
        "Python >= 3.11",
        py_ok,
        f"found {sys.version.split()[0]}" if py_ok else f"found {sys.version.split()[0]} — install 3.11+",
    )

    # --- tomllib available (stdlib, 3.11+) ---
    try:
        import tomllib  # noqa: F401

        check("tomllib available (stdlib)", True)
    except ImportError:
        check("tomllib available (stdlib)", False, "requires Python 3.11+")

    # --- pydantic ---
    try:
        import pydantic

        version = pydantic.VERSION
        check(
            f"pydantic == {EXPECTED_PYDANTIC}",
            version == EXPECTED_PYDANTIC,
            f"found {version}" + ("" if version == EXPECTED_PYDANTIC else " — run: pip install -r requirements.txt"),
        )
    except ImportError:
        check(f"pydantic == {EXPECTED_PYDANTIC}", False, "not installed — run: pip install -r requirements.txt")

    # --- pytest ---
    try:
        import pytest

        version = pytest.__version__
        check(
            f"pytest == {EXPECTED_PYTEST}",
            version == EXPECTED_PYTEST,
            f"found {version}" + ("" if version == EXPECTED_PYTEST else " — run: pip install -r requirements.txt"),
        )
    except ImportError:
        check(f"pytest == {EXPECTED_PYTEST}", False, "not installed — run: pip install -r requirements.txt")

    # --- Required files/directories exist ---
    required_paths = [
        "config/settings.toml",
        "config/fake_llm_scenarios.json",
        "prompts/triage_system.md",
        "prompts/triage_user.md",
        "data/samples",
        "tests/fixtures/llm_responses",
    ]
    for rel in required_paths:
        path = REPO_ROOT / rel
        check(f"exists: {rel}", path.exists(), "" if path.exists() else "missing")

    # --- Config parses ---
    settings = None
    try:
        sys.path.insert(0, str(REPO_ROOT))
        from reqtriage.config import ConfigError, Settings

        try:
            settings = Settings.load(repo_root=REPO_ROOT)
            check("config/settings.toml parses", True)
        except ConfigError as exc:
            check("config/settings.toml parses", False, str(exc))
    except Exception as exc:  # pragma: no cover - defensive
        check("reqtriage package importable", False, str(exc))

    # --- A sample request loads ---
    if settings is not None:
        try:
            import json

            from reqtriage.models import TriageRequest

            sample_path = settings.data.samples_dir / "example_001.json"
            raw = json.loads(sample_path.read_text(encoding="utf-8"))
            TriageRequest.model_validate(raw)
            check("sample request loads (example_001.json)", True)
        except Exception as exc:
            check("sample request loads (example_001.json)", False, str(exc))

    # --- Minimal FakeLLM round trip (no network) ---
    if settings is not None:
        try:
            from reqtriage.agent import run_triage
            from reqtriage.llm.fake import FakeLLM
            from reqtriage.models import TriageRequest

            request = TriageRequest(
                request_id="preflight-smoke-test",
                source="ticket_form",
                description="Preflight smoke test request — safe to ignore.",
            )
            llm = FakeLLM.from_script(
                [
                    '{"action": "final", "result": {"summary": "smoke test", "missing_info": [], '
                    '"confidence": 0.9, "needs_human_review": false, "rationale": "smoke test"}}'
                ]
            )
            result = run_triage(request, llm, settings)
            check("FakeLLM smoke run completes end-to-end", result.request_id == "preflight-smoke-test")
        except Exception as exc:
            check("FakeLLM smoke run completes end-to-end", False, str(exc))

    # --- Report ---
    width = max((len(name) for name, _, _ in _results), default=0)
    all_ok = True
    for name, ok, detail in _results:
        status = "PASS" if ok else "FAIL"
        all_ok = all_ok and ok
        line = f"[{status}] {name.ljust(width)}"
        if detail:
            line += f"  ({detail})"
        print(line)

    print()
    if all_ok:
        print("All checks passed. You're ready for class.")
        return 0
    print("Some checks failed — fix the items above before class. See README.md.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
