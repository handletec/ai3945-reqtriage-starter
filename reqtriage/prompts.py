"""Loading and rendering the two prompt files.

Prompts are treated as versioned engineering artefacts, not inline
strings: they live in `prompts/`, get read here, and their version
number (from `config/settings.toml`, `[prompts] version`) is recorded in
every `RunMeta` so a behavioural change can always be traced back to a
specific prompt revision (see `prompts/CHANGELOG.md`).

Rendering uses plain `.replace()` on distinctive `<<TOKEN>>` markers
rather than `str.format()` — the user prompt embeds a JSON blob, and
`str.format()` treats every `{` and `}` in that JSON as a format field,
which breaks immediately. This is a small, deliberate, teachable choice.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from reqtriage.config import Settings


class PromptError(Exception):
    """A prompt file is missing or a required placeholder was not
    found — a course-authoring mistake, surfaced clearly rather than
    silently sending the model a half-rendered prompt."""


def load_system_prompt(settings: Settings) -> str:
    path = settings.prompts.system_path
    if not path.is_file():
        raise PromptError(f"System prompt file not found: {path}")
    return path.read_text(encoding="utf-8")


def render_user_prompt(
    settings: Settings,
    request_json: dict[str, Any],
    tool_results: list[dict[str, Any]] | None = None,
) -> str:
    path = settings.prompts.user_path
    if not path.is_file():
        raise PromptError(f"User prompt file not found: {path}")
    template = path.read_text(encoding="utf-8")

    rendered = template.replace("<<REQUEST_JSON>>", json.dumps(request_json, indent=2))
    rendered = rendered.replace(
        "<<TOOL_RESULTS_JSON>>", json.dumps(tool_results or [], indent=2)
    )

    if "<<" in rendered and ">>" in rendered:
        # A leftover unresolved token means the template used a marker
        # this function does not know about — fail loudly at authoring
        # time rather than send the model a literal "<<SOMETHING>>".
        raise PromptError(f"Unresolved placeholder remains in rendered prompt: {path}")

    return rendered
