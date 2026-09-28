"""Tests for the LLM boundary contract itself — complete, since
`reqtriage/llm/base.py` is complete."""

from __future__ import annotations

from reqtriage.llm.base import LLMClient, LLMResponse


def test_llm_response_defaults():
    response = LLMResponse(text="hello", model_id="fake-llm-v1")
    assert response.text == "hello"
    assert response.model_id == "fake-llm-v1"
    assert response.prompt_tokens is None
    assert response.completion_tokens is None
    assert response.latency_ms == 0.0


def test_anything_with_a_matching_complete_method_satisfies_llmclient():
    class TinyClient:
        def complete(self, system: str, user: str) -> LLMResponse:
            return LLMResponse(text=f"echo: {user}", model_id="tiny")

    client: LLMClient = TinyClient()
    result = client.complete(system="sys", user="hello")
    assert result.text == "echo: hello"
