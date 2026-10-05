from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path

from copilot import CopilotClient
from copilot.session import PermissionHandler


class CopilotLLM:
    """Runtime model adapter using the participant's signed-in Copilot account."""

    def __init__(self, model: str | None = None) -> None:
        self.model = model or os.getenv("COPILOT_MODEL", "auto")

    def complete(self, system: str, user: str) -> str:
        return asyncio.run(self._complete(system, user))

    async def _complete(self, system: str, user: str) -> str:
        client = CopilotClient(mode="empty")
        await client.start()

        session = None

        try:
            session = await client.create_session(
                on_permission_request=PermissionHandler.approve_all,
                model=self.model,
                available_tools=[],
                system_message={
                    "mode": "replace",
                    "content": system,
                },
            )

            response = await session.send_and_wait(user)

            if response is None:
                raise RuntimeError("Copilot returned no assistant response")

            content = getattr(response.data, "content", None)

            if not content:
                raise RuntimeError("Copilot returned empty assistant content")

            return content
        finally:
            if session is not None:
                await session.disconnect()

            await client.stop()


class FakeLLM:
    """Deterministic scripted model substitute used for repeatable testing."""

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
