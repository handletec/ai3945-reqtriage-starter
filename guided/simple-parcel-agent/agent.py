from __future__ import annotations

"""Participant starter for the simple parcel-agent lab.

The file already contains the boring wiring:
- paths;
- CLI parsing;
- FakeLLM vs optional real-model selection.

Checkpoint 2 asks you to implement only the small L2 orchestration path in
run_agent(). Follow LAB.md rather than inventing a different architecture.
"""

import argparse
import json
import sys
from pathlib import Path

from llm import FakeLLM, OpenAICompatibleLLM


ROOT = Path(__file__).resolve().parent
SYSTEM_PROMPT = ROOT / "prompts" / "system.md"
USER_PROMPT = ROOT / "prompts" / "user.md"
PACKAGE_DATA = ROOT / "data" / "packages.json"
FAKE_RESPONSES = ROOT / "fake_responses.json"

MAX_TOOL_ACTIONS = 1
MAX_MODEL_TURNS = 2


def build_llm(mode: str):
    if mode == "fake":
        return FakeLLM.from_file(FAKE_RESPONSES)
    if mode == "real":
        return OpenAICompatibleLLM()
    raise ValueError(f"Unknown mode: {mode}")


def run_agent(request: str, llm) -> dict:
    """TODO: implement this in LAB.md Checkpoint 2."""
    raise NotImplementedError("Open LAB.md and complete Checkpoint 2.")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "request",
        nargs="?",
        default="My parcel PKG123 was due yesterday. Where is it?",
    )
    parser.add_argument(
        "--mode",
        choices=["fake", "real"],
        default="fake",
    )
    args = parser.parse_args()

    try:
        result = run_agent(args.request, build_llm(args.mode))
    except NotImplementedError as exc:
        print(str(exc))
        return 1
    except (ValueError, json.JSONDecodeError, KeyError) as exc:
        result = {
            "status": "degraded",
            "error": type(exc).__name__,
            "detail": str(exc),
        }

    print("\nFINAL RESULT")
    print(json.dumps(result, indent=2))

    return 0 if result.get("status") == "completed" else 1


if __name__ == "__main__":
    sys.exit(main())
