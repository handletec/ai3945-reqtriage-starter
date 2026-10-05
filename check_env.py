from __future__ import annotations

import importlib.util
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

REQUIRED_FILES = [
    "README.md",
    "LAB.md",
    "COPILOT_PROMPT.md",
    "COPILOT_SETUP.md",
    "CONCEPTS.md",
    "TROUBLESHOOTING.md",
    "agent.py",
    "llm.py",
    "tools.py",
    "model_check.py",
    "fake_responses.json",
    "prompts/system.md",
    "prompts/user.md",
    "data/packages.json",
    "tests/test_agent.py",
    "tests/test_tools.py",
]

REQUIRED_PACKAGES = ["copilot", "pytest"]


def report(label: str, ok: bool, detail: str = "") -> bool:
    state = "PASS" if ok else "FAIL"
    suffix = f" — {detail}" if detail else ""
    print(f"[{state}] {label}{suffix}")
    return ok


def main() -> int:
    results: list[bool] = []

    results.append(
        report(
            "Python >= 3.11",
            sys.version_info >= (3, 11),
            sys.version.split()[0],
        )
    )

    results.append(
        report(
            "Copilot CLI installed",
            shutil.which("copilot") is not None,
            "read COPILOT_SETUP.md",
        )
    )

    for package in REQUIRED_PACKAGES:
        results.append(
            report(
                f"Python package: {package}",
                importlib.util.find_spec(package) is not None,
                "run: python -m pip install -r requirements.txt",
            )
        )

    for relative in REQUIRED_FILES:
        results.append(report(f"file: {relative}", (ROOT / relative).exists()))

    print()

    if all(results):
        print("All local checks passed. Next run: python model_check.py")
        return 0

    print("Fix the FAIL items before continuing.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
