"""Console logging only, AT THIS CHECKPOINT.

Human-readable progress and warnings while a run is happening, via the
stdlib `logging` module, configured once by `configure_console_logging()`.

There is no JSONL run log yet (`logs/runs.jsonl`) — that's worth adding
once there's a `TriageResult` worth recording one line per run about,
which isn't yet.

What NOT to log, enforced by convention here (there is no secret-scanning
magic — reviewers should still check): never log an API key or any
`get_secret()` value.
"""

from __future__ import annotations

import logging

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
