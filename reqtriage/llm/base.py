"""The LLM boundary — COMPLETE at this checkpoint. This is the interface
you'll implement against, not something you need to change.

Every model call in this application should go through exactly one
seam: something that implements `LLMClient.complete()`. Nothing above
this seam should ever know or care whether the concrete implementation
is a scripted fake (which you'll build next — see `llm/fake.py`) or a
real HTTP-backed provider.

This is also where "the model's output is untrusted input" starts:
`LLMResponse.text` is a plain string. Nothing about this boundary
parses it, trusts it, or executes it — whatever you build on top of
this should always treat `.text` as hostile until proven otherwise.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class LLMResponse:
    """What any LLM client hands back, regardless of provider.

    `model_id`, token counts, and latency are runtime facts the *client*
    reports about itself — never something the model's own text gets to
    assert about itself.
    """

    text: str
    model_id: str
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    latency_ms: float = 0.0


class LLMClient(Protocol):
    """The one interface every provider must satisfy. Deliberately just
    one method: you don't need streaming, multi-turn chat history
    management, or native function calling to build the agent loop in
    later exercises — each full turn is one independent `complete()`
    call."""

    def complete(self, system: str, user: str) -> LLMResponse:
        """Send one system+user prompt pair, get one raw text response
        back. Implementations must not raise for a "the model said
        something silly" case — that's expected, and handling it is a
        later exercise. Implementations SHOULD raise for a genuine
        infrastructure failure (timeout, connection refused, auth
        failure)."""
        ...
