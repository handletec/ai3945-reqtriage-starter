"""Two kinds of logging, kept deliberately separate:

* Console logging (stdlib `logging`) — human-readable progress and
  warnings while a run is happening. Configured once by
  `configure_console_logging()`.
* The JSONL run log (`logs/runs.jsonl`) — one machine-readable record per
  run, written by `append_run_log()`. This is what Module 5 teaches you
  to read when diagnosing a regression: grep it by request id, prompt
  version, or outcome.

What NOT to log, enforced by convention here (there is no secret-scanning
magic — reviewers should still check): never log an API key or any
`get_secret()` value, and never log the full free-text request
description by default (the summary/rationale/error fields are already
short and are what go in the log; the raw description is not added to
the JSONL record).
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

_LOGGER_NAME = "reqtriage"


def configure_console_logging(level: str = "INFO") -> logging.Logger:
    logger = logging.getLogger(_LOGGER_NAME)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(levelname)s %(name)s: %(message)s"))
        logger.addHandler(handler)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    logger.propagate = False
    return logger


def get_logger() -> logging.Logger:
    return logging.getLogger(_LOGGER_NAME)


def append_run_log(record: dict[str, Any], log_path: Path) -> None:
    """Append one JSON line to the run log. Creates the parent directory
    if needed (a fresh checkout has no `logs/` contents beyond
    `.gitkeep`). Never raises on a logging failure in a way that would
    take down the run itself — logging is best-effort telemetry, not a
    correctness requirement — but DOES surface the problem on the
    console logger so it is not silently lost.
    """

    try:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, sort_keys=True) + "\n")
    except OSError as exc:  # pragma: no cover - defensive, not exercised in tests
        get_logger().warning("Could not write to run log %s: %s", log_path, exc)
