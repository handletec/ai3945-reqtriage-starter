from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

REQUIRED_FILES = [
    "README.md",
    "LAB.md",
    "COPILOT_PROMPT.md",
    "MODEL_SETUP.md",
    "agent.py",
    "llm.py",
    "tools.py",
    "model_check.py",
    "prompts/system.md",
    "prompts/user.md",
    "data/packages.json",
]

REQUIRED_PACKAGES = ["anthropic", "dotenv", "pytest"]


def report(label: str, ok: bool, detail: str = "") -> bool:
    state = "PASS" if ok else "FAIL"
    suffix = f" — {detail}" if detail else ""
    print(f"[{state}] {label}{suffix}")
    return ok


def load_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}

    if not path.exists():
        return values

    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()

        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()

    return values


def main() -> int:
    results: list[bool] = []

    results.append(
        report(
            "Python >= 3.11",
            sys.version_info >= (3, 11),
            sys.version.split()[0],
        )
    )

    for package in REQUIRED_PACKAGES:
        results.append(
            report(
                f"package: {package}",
                importlib.util.find_spec(package) is not None,
                "run: python -m pip install -r requirements.txt",
            )
        )

    for relative in REQUIRED_FILES:
        results.append(report(f"file: {relative}", (ROOT / relative).exists()))

    env_file = ROOT / ".env"
    env_values = load_env_file(env_file)

    results.append(
        report(
            "file: .env",
            env_file.exists(),
            "copy .env.example to .env",
        )
    )

    api_key = os.getenv("ANTHROPIC_API_KEY", "").strip() or env_values.get(
        "ANTHROPIC_API_KEY", ""
    ).strip()

    model = os.getenv("ANTHROPIC_MODEL", "").strip() or env_values.get(
        "ANTHROPIC_MODEL", ""
    ).strip()

    results.append(
        report(
            "ANTHROPIC_API_KEY set",
            bool(api_key),
            "ask trainer for runtime credentials",
        )
    )

    results.append(
        report(
            "ANTHROPIC_MODEL set",
            bool(model),
            "ask trainer for model name",
        )
    )

    print()

    if all(results):
        print("All checks passed. Continue with LAB.md.")
        return 0

    print("Fix the FAIL items before continuing.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
