"""Command-line entry point: `python -m reqtriage <request.json>`.

This is scaffolding, not a finished CLI. It currently does the plumbing
you don't need to build yourself — argument parsing, loading and
validating a request file, clear exit codes for a bad file — and stops
right before the part that needs `FakeLLM` (which doesn't exist yet; see
`reqtriage/llm/fake.py`).

Exit codes:

  0  The request file loaded and validated successfully.
  1  Usage or environment problem: bad arguments, missing/unreadable
     request file, or invalid/schema-violating request JSON.

Once you've implemented `FakeLLM`, the natural next step (part of the
same exercise, or the one right after it — check the course material)
is to build the request into a prompt, call `llm.complete()`, and print
the raw response instead of the request below. Work that structure out
from `reqtriage/llm/base.py`'s docstring rather than guessing at it.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from pydantic import ValidationError

from reqtriage.config import Settings
from reqtriage.logging_setup import configure_console_logging
from reqtriage.models import TriageRequest


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m reqtriage",
        description="Load and validate one TriageRequest JSON file. (Calling a model comes next.)",
    )
    parser.add_argument("request_path", type=Path, help="Path to a TriageRequest JSON file")
    parser.add_argument("--verbose", action="store_true", help="Console log at DEBUG level")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    configure_console_logging("DEBUG" if args.verbose else "INFO")

    # Settings.load() is complete scaffolding — see reqtriage/config.py.
    # You don't need to change it for this checkpoint.
    _settings = Settings.load()

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

    # TODO (next exercise): once reqtriage/llm/fake.py is implemented,
    # build a FakeLLM, render a prompt from `request`, call
    # `llm.complete(system=..., user=...)`, and print its raw response
    # instead of the loaded request below.
    print(json.dumps(request.model_dump(mode="json"), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":  # pragma: no cover - exercised via __main__.py
    sys.exit(main())
