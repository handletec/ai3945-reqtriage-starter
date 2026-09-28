"""Command-line entry point: `python -m reqtriage <request.json>`.

Exit codes (checked in tests/test_cli.py and documented in README.md):

  0  A normal `TriageResult` was produced (no software failure). Whether
     `needs_human_review` is true or false is a normal *business*
     outcome, not a reason for a non-zero exit — plenty of valid triage
     results need a human to look at them.
  1  Usage or environment problem: bad arguments, missing/unreadable
     request file, invalid request JSON, or a configuration error. The
     agent never ran.
  2  The agent ran but could not produce a normal result — a *degraded*
     `TriageResult` was produced instead (`result.error` is set). The
     output on stdout is still a single valid JSON object; nothing
     "crashed", but a human should look at why.

This module only does wiring: argument parsing, building the settings and
LLM client, calling `agent.run_triage`, and printing/exiting. It has no
triage logic of its own — that is `agent.py`'s job, which is what keeps
`run_triage()` independently testable without a CLI.
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import sys
from pathlib import Path

from pydantic import ValidationError

from reqtriage.config import ConfigError, Settings
from reqtriage.llm.base import LLMClient
from reqtriage.llm.fake import FakeLLM
from reqtriage.llm.http import HttpLLM
from reqtriage.logging_setup import configure_console_logging
from reqtriage.models import TriageRequest


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m reqtriage",
        description="Run the reqtriage agent against one request JSON file.",
    )
    parser.add_argument("request_path", type=Path, help="Path to a TriageRequest JSON file")
    parser.add_argument(
        "--config", type=Path, default=None, help="Path to settings.toml (default: config/settings.toml)"
    )
    parser.add_argument(
        "--max-tool-actions",
        type=int,
        default=None,
        help="Override config/settings.toml agent.max_tool_actions (the L1/L2/L3 dial)",
    )
    parser.add_argument(
        "--max-model-turns",
        type=int,
        default=None,
        help="Override config/settings.toml agent.max_model_turns (the runaway-loop safety bound)",
    )
    parser.add_argument(
        "--log-path",
        type=Path,
        default=None,
        help="Override config/settings.toml logging.log_path (mainly for tests/validation, to avoid writing into a shared logs/runs.jsonl)",
    )
    parser.add_argument("--verbose", action="store_true", help="Console log at DEBUG level")
    return parser


def _build_fake_llm(settings: Settings, request_id: str) -> FakeLLM:
    scenario_name = settings.fake_llm.default_scenario
    if settings.fake_llm.scenario_map_path.is_file():
        mapping = json.loads(settings.fake_llm.scenario_map_path.read_text(encoding="utf-8"))
        scenario_name = mapping.get(request_id, scenario_name)
    fixture_path = settings.fake_llm.fixtures_dir / f"{scenario_name}.json"
    return FakeLLM.from_fixture_file(fixture_path, model_id=settings.llm.model_id)


def build_llm_client(settings: Settings, request_id: str) -> LLMClient:
    if settings.llm.provider == "fake":
        return _build_fake_llm(settings, request_id)
    if settings.llm.provider == "http":
        return HttpLLM()  # raises HttpLLMNotConfiguredError — see llm/http.py
    raise ConfigError(f"Unknown llm.provider: {settings.llm.provider!r}")


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    configure_console_logging("DEBUG" if args.verbose else "INFO")

    try:
        settings = Settings.load(config_path=args.config)
    except ConfigError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 1

    if args.max_tool_actions is not None or args.max_model_turns is not None:
        new_max_tool_actions = args.max_tool_actions if args.max_tool_actions is not None else settings.agent.max_tool_actions
        new_max_model_turns = args.max_model_turns if args.max_model_turns is not None else settings.agent.max_model_turns
        if new_max_model_turns <= new_max_tool_actions:
            print(
                "Configuration error: --max-model-turns must be greater than --max-tool-actions "
                f"(got max_tool_actions={new_max_tool_actions}, max_model_turns={new_max_model_turns})",
                file=sys.stderr,
            )
            return 1
        settings = dataclasses.replace(
            settings,
            agent=dataclasses.replace(
                settings.agent, max_tool_actions=new_max_tool_actions, max_model_turns=new_max_model_turns
            ),
        )

    if args.log_path is not None:
        settings = dataclasses.replace(
            settings, logging=dataclasses.replace(settings.logging, log_path=args.log_path)
        )

    if not args.request_path.is_file():
        print(f"Request file not found: {args.request_path}", file=sys.stderr)
        return 1

    try:
        raw = json.loads(args.request_path.read_text(encoding="utf-8"))
        request = TriageRequest.model_validate(raw)
    except json.JSONDecodeError as exc:
        print(f"Request file is not valid JSON: {exc}", file=sys.stderr)
        return 1
    except ValidationError as exc:
        print(f"Request file does not match the TriageRequest schema:\n{exc}", file=sys.stderr)
        return 1

    try:
        llm = build_llm_client(settings, request.request_id)
    except Exception as exc:
        print(f"Could not build LLM client: {exc}", file=sys.stderr)
        return 1

    from reqtriage.agent import run_triage  # local import keeps CLI import time small

    result = run_triage(request, llm, settings)
    print(json.dumps(result.model_dump(mode="json"), indent=2, sort_keys=True))

    return 2 if result.error else 0


if __name__ == "__main__":  # pragma: no cover - exercised via __main__.py
    sys.exit(main())
