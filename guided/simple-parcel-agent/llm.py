from __future__ import annotations

import json
import os
import urllib.request
from pathlib import Path


class FakeLLM:
    """Return scripted model responses in a predictable order."""

    def __init__(self, responses: list[str]) -> None:
        if not responses:
            raise ValueError("FakeLLM requires at least one response")

        self.responses = responses
        self.index = 0
        self.calls: list[tuple[str, str]] = []

    @classmethod
    def from_file(cls, path: Path) -> "FakeLLM":
        data = json.loads(path.read_text(encoding="utf-8"))
        return cls(data["responses"])

    def complete(self, system: str, user: str) -> str:
        self.calls.append((system, user))
        index = min(self.index, len(self.responses) - 1)
        response = self.responses[index]
        self.index += 1
        return response


class OpenAICompatibleLLM:
    """Optional adapter for a trainer-provided OpenAI-compatible endpoint."""

    def __init__(self) -> None:
        self.url = os.environ["LLM_URL"]
        self.model = os.environ["LLM_MODEL"]
        self.api_key = os.environ.get("LLM_API_KEY", "")

    def complete(self, system: str, user: str) -> str:
        payload = json.dumps({
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }).encode("utf-8")

        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        request = urllib.request.Request(
            self.url,
            data=payload,
            headers=headers,
            method="POST",
        )

        with urllib.request.urlopen(request, timeout=30) as response:
            body = json.loads(response.read().decode("utf-8"))

        return body["choices"][0]["message"]["content"]
