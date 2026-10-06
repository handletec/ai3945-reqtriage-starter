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
from tools import get_depot_info, track_package


ROOT = Path(__file__).resolve().parent
SYSTEM_PROMPT = ROOT / "prompts" / "system.md"
USER_PROMPT = ROOT / "prompts" / "user.md"
FAKE_RESPONSES = {
    "l2": ROOT / "fake_responses_l2.json",
    "l3": ROOT / "fake_responses_l3.json",
}
FENCE = "`" * 3

LEVELS = {
    "l2": {
        "max_tool_actions": 1,
        "max_model_turns": 2,
        "allowed_tools": {"track_package"},
    },
    "l3": {
        "max_tool_actions": 2,
        "max_model_turns": 3,
        "allowed_tools": {"track_package", "get_depot_info"},
    },
}


def render_user_prompt(request: str, tool_result: str) -> str:
    template = USER_PROMPT.read_text(encoding="utf-8")
    return (
        template
        .replace("{{request}}", request)
        .replace("{{tool_result}}", tool_result)
    )


def build_system_prompt(level: str) -> str:
    config = LEVELS[level]
    base = SYSTEM_PROMPT.read_text(encoding="utf-8")
    allowed = ", ".join(sorted(config["allowed_tools"]))

    authority = (
        "\n\n# Runtime Authority\n\n"
        f"Autonomy level: {level.upper()}\n"
        f"Allowed tools: {allowed}\n"
        f"Maximum tool actions: {config['max_tool_actions']}\n"
        f"Maximum model turns: {config['max_model_turns']}\n\n"
        "Do not request a tool that is not in Allowed tools. "
        "If the available authority is insufficient to fully answer the request, "
        "return a final answer that clearly states what is known and what cannot "
        "be verified under the current authority."
    )

    return base + authority


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
    level: str,
    model_turns: int,
    tool_actions: int,
    detail: str | None = None,
) -> dict:
    result = {
        "status": "degraded",
        "level": level.upper(),
        "error": error,
        "model_turns": model_turns,
        "tool_actions": tool_actions,
    }

    if detail:
        result["detail"] = detail

    return result


def execute_tool(tool_name: str, arguments: dict) -> tuple[str, dict]:
    if tool_name == "track_package":
        tracking_id = arguments.get("tracking_id")

        if not isinstance(tracking_id, str) or not tracking_id.strip():
            raise ValueError("tracking_id must be a non-empty string")

        tracking_id = tracking_id.strip()
        return (
            f"track_package({tracking_id!r})",
            track_package(tracking_id),
        )

    if tool_name == "get_depot_info":
        depot_name = arguments.get("depot_name")

        if not isinstance(depot_name, str) or not depot_name.strip():
            raise ValueError("depot_name must be a non-empty string")

        depot_name = depot_name.strip()
        return (
            f"get_depot_info({depot_name!r})",
            get_depot_info(depot_name),
        )

    raise ValueError(f"Unsupported tool: {tool_name}")


def run_agent(request: str, llm, level: str = "l2") -> dict:
    if level not in LEVELS:
        raise ValueError(f"Unsupported autonomy level: {level}")

    config = LEVELS[level]
    system = build_system_prompt(level)
    tool_history: list[dict] = []
    model_turns = 0
    tool_actions = 0

    for _ in range(config["max_model_turns"]):
        tool_result = (
            "No tool has been run yet."
            if not tool_history
            else json.dumps(tool_history, indent=2)
        )
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
                level=level,
                model_turns=model_turns,
                tool_actions=tool_actions,
                detail=str(exc),
            )

        if action["action"] == "final":
            answer = action.get("answer")

            if not isinstance(answer, str) or not answer.strip():
                return degraded(
                    "invalid_final_answer",
                    level=level,
                    model_turns=model_turns,
                    tool_actions=tool_actions,
                )

            return {
                "status": "completed",
                "level": level.upper(),
                "answer": answer.strip(),
                "model_turns": model_turns,
                "tool_actions": tool_actions,
            }

        tool_name = action.get("tool")

        if tool_name not in config["allowed_tools"]:
            return degraded(
                "tool_not_allowed",
                level=level,
                model_turns=model_turns,
                tool_actions=tool_actions,
                detail=f"Requested tool: {tool_name!r}",
            )

        if tool_actions >= config["max_tool_actions"]:
            return degraded(
                "tool_budget_exhausted",
                level=level,
                model_turns=model_turns,
                tool_actions=tool_actions,
            )

        arguments = action.get("arguments")

        if not isinstance(arguments, dict):
            return degraded(
                "invalid_tool_arguments",
                level=level,
                model_turns=model_turns,
                tool_actions=tool_actions,
                detail="arguments must be a JSON object",
            )

        try:
            display, tool_output = execute_tool(tool_name, arguments)
        except ValueError as exc:
            return degraded(
                "invalid_tool_arguments",
                level=level,
                model_turns=model_turns,
                tool_actions=tool_actions,
                detail=str(exc),
            )

        tool_actions += 1

        print("\nTOOL")
        print(display)
        print(json.dumps(tool_output, indent=2))

        tool_history.append({
            "tool": tool_name,
            "result": tool_output,
        })

    return degraded(
        "model_turn_budget_exhausted",
        level=level,
        model_turns=model_turns,
        tool_actions=tool_actions,
    )


def build_llm(
    mode: str,
    *,
    level: str,
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
        return FakeLLM.from_file(FAKE_RESPONSES[level])

    raise ValueError(f"Unsupported mode: {mode}")


def print_authority(level: str) -> None:
    config = LEVELS[level]
    tools = ", ".join(sorted(config["allowed_tools"]))

    print(f"AUTONOMY LEVEL: {level.upper()}")
    print(f"Allowed tools: {tools}")
    print(f"Tool-action budget: {config['max_tool_actions']}")
    print(f"Model-turn budget: {config['max_model_turns']}")


def main() -> int:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "request",
        nargs="?",
        default="My parcel PKG123 is delayed. Can I collect it from the depot today?",
    )

    parser.add_argument(
        "--level",
        choices=sorted(LEVELS),
        default="l2",
        help="Autonomy level to demonstrate",
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
        print_authority(args.level)

        llm = build_llm(
            args.mode,
            level=args.level,
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

        result = run_agent(args.request, llm, level=args.level)

    except Exception as exc:
        result = {
            "status": "degraded",
            "level": args.level.upper(),
            "error": type(exc).__name__,
            "detail": str(exc),
        }

    print("\nFINAL RESULT")
    print(json.dumps(result, indent=2))

    return 0 if result.get("status") == "completed" else 1


if __name__ == "__main__":
    sys.exit(main())
