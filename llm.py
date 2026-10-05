from __future__ import annotations

import os

from anthropic import Anthropic


class AnthropicLLM:
    """Small runtime adapter around the Anthropic Messages API."""

    def __init__(self) -> None:
        self.api_key = os.environ["ANTHROPIC_API_KEY"]
        self.model = os.environ["ANTHROPIC_MODEL"]
        self.client = Anthropic(api_key=self.api_key)

    def complete(self, system: str, user: str) -> str:
        response = self.client.messages.create(
            model=self.model,
            max_tokens=500,
            system=system,
            messages=[
                {"role": "user", "content": user},
            ],
        )

        parts = [
            block.text
            for block in response.content
            if getattr(block, "type", None) == "text"
        ]

        if not parts:
            raise RuntimeError("Model returned no text content")

        return "".join(parts)
