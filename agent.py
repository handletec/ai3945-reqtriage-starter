from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from llm import (
    DEFAULT_EFFORT,
    DEFAULT_MAX_TOKENS,
    DEFAULT_MODEL,
    AnthropicLLM,
    FakeLLM,
    VALID_EFFORTS,
)
from tools import track_package


ROOT = Path(__file__).resolve().parent
SystemPrompt = ROOT / "prompts" / "system.md"
UserPrompt = ROOT / "prompts" / "user.md"
PACKAGE_DATA = ROOT / "data" / "packages.json"
FAKE_RESPONSES = ROOT / "fake_responses.json"

MAX_TOOL_ACTIONS = 1
MAX_MODEL_TURNS = 2
FENCE = "`" * 3


def render_user_prompt(request: str, tool_result: str) -> str:
    template = UserPrompt.read_text(encoding="utf-8")
    return (
        template
        .replace("{{request}}", request)
        .replace("{{tool_result}}", tool_result)
    )


def parse_action(raw: str) -> dict:
    text = raw.strip()

    if text.startswith(FENCE):
        lines = text.splitlines()
        if lines and lines[0].startswith(FENCE):
            lines = lines[1:]
        if lines and lines[-1].strip() == FENCE:
            lines = lines[:-1]
        text = "\n".join(lines).strip()

    action = json.loads(text)
    if not isinstance(action, dict):
        raise ValueError("Model action must be a JSON object")
    if action.get("action") not in {"call_tool", "final"}:
        raise ValueError("Unsupported model action")
    return action


def degraded(
    error: str,
    *,
    model_turns: int,
    tool_actions: int,
    detail: str | None = None,
) -> dict:
    result = {
        "status": "degraded",
        "error": error,
        "model_turns": model_turns,
        "tool_actions": tool_actions,
    }
    if detail:
        result["detail"] = detail
    return result


def run_agent(request: str, llm) -> dict:
    system = SystemPrompt.read_text(encoding="utf-8")
    tool_result = "No tool has been run yet."
    model_turns = 0
    tool_actions = 0

    for _ in range(MAX_MODEL_TURNS):
        rendered_user = render_user_prompt(request, tool_result)
        model_turns += 1
        raw = llm.complete(system, rendered_user)

        print(f"\nMODEL TURN {model_turns}")
        print(raw)

        try:
            action = parse_action(raw)
        except (json.JSONDecodeError, ValueError) as exc:
            return degraded(
                "invalid_model_output",
                model_turns=model_turns,
                tool_actions=tool_actions,
                detail=str(exc),
            )

        if action["action"] == "final":
            answer = action.get("answer")
            if not isinstance(answer, str) or not answer.strip():
                return degraded(
                    "invalid_final_answer",
                    model_turns=model_turns,
                    tool_actions=tool_actions,
                )
            return {
                "status": "completed",
                "answer": answer.strip(),
                "model_turns": model_turns,
                "tool_actions": tool_actions,
            }

        if tool_actions >= MAX_TOOL_ACTIONS:
            return degraded(
                "tool_budget_exhausted",
                model_turns=model_turns,
                tool_actions=tool_actions,
            )

        tool_name = action.get("tool")
        if tool_name != "track_package":
            return degraded(
                "tool_not_allowed",
                model_turns=model_turns,
                tool_actions=tool_actions,
                detail=f"Requested tool: {tool_name!r}",
            )

        arguments = action.get("arguments")
        if not isinstance(arguments, dict):
            return degraded(
                "invalid_tool_arguments",
                model_turns=model_turns,
                tool_actions=tool_actions,
                detail="arguments must be a JSON object",
            )

        tracking_id = arguments.get("tracking_id")
        if not isinstance(tracking_id, str) or not tracking_id.strip():
            return degraded(
                "invalid_tool_arguments",
                model_turns=model_turns,
                tool_actions=tool_actions,
                detail="tracking_id must be a non-empty string",
            )

        tracking_id = tracking_id.strip()
        tool_output = track_package(tracking_id, PACKAGE_DATA)
        tool_actions += 1

        print("\nTOOL")
        print(f"track_package({tracking_id!r})")
        print(json.dumps(tool_output, indent=2))

        tool_result = json.dumps(tool_output)

    return degraded(
        "model_turn_budget_exhausted",
        model_turns=model_turns,
        tool_actions=tool_actions,
    )


def build_llm(
    mode: str,
    *,
    model: str | None,
    effort: str | None,
    max_tokens: int | None,
):
    if mode == "claude":
        return AnthropicLLM(
            model=model,
            effort=effort,
            max_tokens=max_tokens,
        )
    if mode == "fake":
        return FakeLLM.from_file(FAKE_RESPONSES)
    raise ValueError(f"Unsupported mode: {mode}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "request",
        nargs="?",
        default="My parcel PKG123 was due yesterday. Where is it?",
    )
    parser.add_argument(
        "--mode",
        choices=["claude", "fake"],
        default="claude",
        help="Runtime model: real Claude API or deterministic FakeLLM",
    )
    parser.add_argument(
        "--model",
        default=None,
        help=f"Claude model ID. Default: ANTHROPIC_MODEL or {DEFAULT_MODEL}",
    )
    parser.add_argument(
        "--effort",
        choices=sorted(VALID_EFFORTS),
        default=None,
        help=f"Claude effort. Default: ANTHROPIC_EFFORT or {DEFAULT_EFFORT}",
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=None,
        help=f"Max response tokens. Default: ANTHROPIC_MAX_TOKENS or {DEFAULT_MAX_TOKENS}",
    )
    args = parser.parse_args()

    try:
        llm = build_llm(
            args.mode,
            model=args.model,
            effort=args.effort,
            max_tokens=args.max_tokens,
        )

        if args.mode == "claude":
            print(
                "CLAUDE RUNTIME "
                f"model={llm.model} "
                f"effort={llm.effort} "
                f"max_tokens={llm.max_tokens}"
            )

        result = run_agent(args.request, llm)
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
