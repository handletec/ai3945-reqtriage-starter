"""The LLM boundary.

Every model call in this application goes through exactly one seam:
something that implements `LLMClient.complete()`. Nothing above this
seam — `agent.py`, `validation.py`, `rules.py` — knows or cares whether
the concrete implementation is `FakeLLM` (this reference build) or a real
HTTP-backed provider (not implemented yet; see `llm/http.py`).

This is also where "the model's output is untrusted input" is made
concrete: `LLMResponse.text` is a plain string. Nothing about this
boundary parses it, trusts it, or executes it — that is
`reqtriage.validation`'s job, and it always treats `.text` as hostile
until proven otherwise.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class LLMResponse:
    """What any LLM client hands back, regardless of provider.

    `model_id`, token counts, and latency are runtime facts the *client*
    reports about itself — they end up in `RunMeta`, not in anything the
    model's own text is trusted to assert.
    """

    text: str
    model_id: str
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    latency_ms: float = 0.0


class LLMClient(Protocol):
    """The one interface every provider must satisfy. Deliberately just
    one method: this course does not need streaming, multi-turn chat
    history management, or native function calling to teach the agent
    loop — each full turn is one independent `complete()` call, and
    `agent.py` is the only place that stitches turns together."""

    def complete(self, system: str, user: str) -> LLMResponse:
        """Send one system+user prompt pair, get one raw text response
        back. Implementations must not raise for a "the model said
        something silly" case — that is expected and handled by
        `reqtriage.validation`. Implementations SHOULD raise for a
        genuine infrastructure failure (timeout, connection refused,
        auth failure) — `agent.py` treats any such exception as a fatal
        run failure and degrades safely."""
        ...
