from __future__ import annotations

import json
import os
from pathlib import Path

from anthropic import Anthropic


DEFAULT_MODEL = "claude-sonnet-5-5"
DEFAULT_EFFORT = "medium"
DEFAULT_MAX_TOKENS = 4096
VALID_EFFORTS = {"low", "medium", "high", "xhigh", "max"}


class AnthropicLLM:
    """Runtime adapter for Claude through the Anthropic Messages API."""

    def __init__(
        self,
        *,
        model: str | None = None,
        effort: str | None = None,
        max_tokens: int | None = None,
    ) -> None:
        self.model = model or os.getenv("ANTHROPIC_MODEL", DEFAULT_MODEL)
        self.effort = effort or os.getenv("ANTHROPIC_EFFORT", DEFAULT_EFFORT)

        if self.effort not in VALID_EFFORTS:
            raise ValueError(
                f"Unsupported effort: {self.effort}. "
                f"Choose one of: {', '.join(sorted(VALID_EFFORTS))}"
            )

        raw_max_tokens = os.getenv(
            "ANTHROPIC_MAX_TOKENS",
            str(DEFAULT_MAX_TOKENS),
        )

        self.max_tokens = (
            max_tokens if max_tokens is not None else int(raw_max_tokens)
        )

        if self.max_tokens < 256:
            raise ValueError("max_tokens must be at least 256")

        self.client = Anthropic(
            api_key=os.environ["ANTHROPIC_API_KEY"]
        )

    def complete(self, system: str, user: str) -> str:
        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=system,
            output_config={
                "effort": self.effort,
            },
            messages=[
                {
                    "role": "user",
                    "content": user,
                }
            ],
        )

        parts = [
            block.text
            for block in response.content
            if getattr(block, "type", None) == "text"
        ]

        if not parts:
            raise RuntimeError("Claude returned no text content")

        return "".join(parts)


class FakeLLM:
    """Deterministic scripted model substitute for repeatable demos/tests."""

    def __init__(self, responses: list[str]) -> None:
        if not responses:
            raise ValueError("FakeLLM requires at least one response")

        self.responses = responses
        self.index = 0

    @classmethod
    def from_file(cls, path: Path) -> "FakeLLM":
        payload = json.loads(path.read_text(encoding="utf-8"))

        if not isinstance(payload, list):
            raise ValueError("FakeLLM response file must contain a JSON list")

        responses = [
            item if isinstance(item, str) else json.dumps(item)
            for item in payload
        ]

        return cls(responses)

    def complete(self, system: str, user: str) -> str:
        if self.index >= len(self.responses):
            return self.responses[-1]

        response = self.responses[self.index]
        self.index += 1
        return response
