from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from dotenv import load_dotenv

from llm import AnthropicLLM
from tools import track_package


ROOT = Path(__file__).resolve().parent
SYSTEM_PROMPT = ROOT / "prompts" / "system.md"
USER_PROMPT = ROOT / "prompts" / "user.md"
PACKAGE_DATA = ROOT / "data" / "packages.json"

MAX_TOOL_ACTIONS = 1
MAX_MODEL_TURNS = 2


def render_user_prompt(request: str, tool_result: str) -> str:
    template = USER_PROMPT.read_text(encoding="utf-8")

    return (
        template
        .replace("{{request}}", request)
        .replace("{{tool_result}}", tool_result)
    )


def parse_action(raw: str) -> dict:
    text = raw.strip()

    if text.startswith("```"):
        lines = text.splitlines()

        if lines and lines[0].startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        text = "\n".join(lines).strip()

    action = json.loads(text)

    if not isinstance(action, dict):
        raise ValueError("Model action must be a JSON object")

    if action.get("action") not in {"call_tool", "final"}:
        raise ValueError("Unsupported model action")

    return action


def run_agent(request: str, llm) -> dict:
    """TODO: implement this function during LAB.md Checkpoint 4."""

    raise NotImplementedError(
        "run_agent() is not implemented yet. Follow LAB.md Checkpoint 4."
    )


def main() -> int:
    load_dotenv()

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "request",
        nargs="?",
        default="My parcel PKG123 was due yesterday. Where is it?",
    )

    args = parser.parse_args()

    try:
        result = run_agent(args.request, AnthropicLLM())

    except NotImplementedError as exc:
        print(str(exc))
        return 1

    except Exception as exc:
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
