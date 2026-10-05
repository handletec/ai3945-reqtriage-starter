from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

REQUIRED = [
    "README.md",
    "LAB.md",
    "CONCEPTS.md",
    "TROUBLESHOOTING.md",
    "agent.py",
    "llm.py",
    "tools.py",
    "fake_responses.json",
    "prompts/system.md",
    "prompts/user.md",
    "data/packages.json",
]


def check(label: str, ok: bool, detail: str = "") -> bool:
    state = "PASS" if ok else "FAIL"
    suffix = f" — {detail}" if detail else ""
    print(f"[{state}] {label}{suffix}")
    return ok


def main() -> int:
    results: list[bool] = []

    results.append(
        check(
            "Python >= 3.11",
            sys.version_info >= (3, 11),
            sys.version.split()[0],
        )
    )

    pytest_available = importlib.util.find_spec("pytest") is not None
    results.append(
        check(
            "pytest installed",
            pytest_available,
            "run: python -m pip install -r requirements.txt" if not pytest_available else "",
        )
    )

    for relative in REQUIRED:
        results.append(check(f"exists: {relative}", (ROOT / relative).exists()))

    print()
    if all(results):
        print("All checks passed. Open LAB.md and start at Checkpoint 1.")
        return 0

    print("Fix the failed checks before starting the lab.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
