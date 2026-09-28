"""FakeLLM — a hand-written, deterministic stand-in for a real model.

Why a hand-written fake instead of a mocking library: the fake's whole
job is to replay realistic *model misbehaviour* (malformed JSON, an
unknown tool name, a script that never says "final") in a way a
participant can open, read, and edit like any other data file. A mock
object hides that behind test-framework machinery; a fixture file makes
it a first-class, inspectable teaching artefact.

IMPORTANT — read this before trusting a green test suite:
FakeLLM tests prove that OUR CODE — the parsing, validation, tool
dispatch, post-rules, and failure handling in this repository — behaves
correctly for a given model response. They prove NOTHING about whether a
real model would produce a *good* triage judgement for a given request.
Testing that requires periodically running representative samples against
a real, approved model and reviewing the output by hand (see README.md,
"Moving to a real provider").

Replay model: a `FakeLLM` is constructed from an ordered list of script
items (a "script"). Each call to `.complete()` returns the next item.
Once the script is exhausted, the LAST item is repeated indefinitely —
this is a deliberate, documented behaviour, not a bug: it is what lets
one canned "call_tool" response stand in for "the model never stops
asking for tools", used to test `max_model_turns` / `max_tool_actions`
termination without writing an absurdly long fixture file.

A script item is either:

* a plain `str` — the response text, with token usage APPROXIMATED from
  the actual system/user/response text length (see `_approx_tokens`).
  This is what every fixture file under `tests/fixtures/llm_responses/`
  uses; it is good enough for scenario tests that don't care about exact
  token math.
* a `ScriptedResponse` — response text PLUS explicit `prompt_tokens` /
  `completion_tokens` (either of which may be `None`, to simulate a
  provider that reports no usage for that call). Use this whenever a
  test needs deterministic, exact usage totals to assert against —
  `RunMeta`'s token totals are a sum across every real model call this
  run makes (see `reqtriage/agent.py::_ModelUsage`), and asserting that
  sum against real prompt/response text lengths would be fragile and
  unreadable; scripting the numbers directly is not.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path

from reqtriage.llm.base import LLMResponse


class FakeLLMExhaustedError(Exception):
    """Raised only if a script is empty at construction time — an
    authoring mistake in a fixture file, not a normal runtime condition."""


@dataclass(frozen=True)
class ScriptedResponse:
    """One script item with EXPLICIT token usage, for tests that need
    deterministic totals — see this module's docstring. `prompt_tokens`
    / `completion_tokens` are passed straight through to `LLMResponse`
    unchanged, including `None`."""

    text: str
    prompt_tokens: int | None = None
    completion_tokens: int | None = None


class FakeLLM:
    def __init__(self, script: list["str | ScriptedResponse"], model_id: str = "fake-llm-v1") -> None:
        if not script:
            raise FakeLLMExhaustedError("FakeLLM script must contain at least one response")
        self._script = list(script)
        self._index = 0
        self.model_id = model_id
        self.calls: list[tuple[str, str]] = []  # (system, user) pairs, for test assertions

    def complete(self, system: str, user: str) -> LLMResponse:
        started = time.monotonic()
        self.calls.append((system, user))
        item = self._script[min(self._index, len(self._script) - 1)]
        self._index += 1
        latency_ms = (time.monotonic() - started) * 1000.0

        if isinstance(item, ScriptedResponse):
            return LLMResponse(
                text=item.text,
                model_id=self.model_id,
                prompt_tokens=item.prompt_tokens,
                completion_tokens=item.completion_tokens,
                latency_ms=latency_ms,
            )

        response_text = item
        return LLMResponse(
            text=response_text,
            model_id=self.model_id,
            prompt_tokens=_approx_tokens(system) + _approx_tokens(user),
            completion_tokens=_approx_tokens(response_text),
            latency_ms=latency_ms,
        )

    @classmethod
    def from_script(cls, script: list["str | ScriptedResponse"], model_id: str = "fake-llm-v1") -> "FakeLLM":
        """Build a FakeLLM directly from in-memory script items (plain
        strings, `ScriptedResponse`s, or a mix). Preferred in unit tests
        where the exact response text — or exact token usage — is the
        point of the test and should be visible next to the assertion."""

        return cls(script, model_id=model_id)

    @classmethod
    def from_fixture_file(cls, path: Path, model_id: str = "fake-llm-v1") -> "FakeLLM":
        """Build a FakeLLM from a named fixture file: a JSON document
        `{"responses": ["...", "..."]}` under
        tests/fixtures/llm_responses/. Used by the CLI (via
        config/fake_llm_scenarios.json) and by tests that want a named,
        reusable scenario rather than an inline script."""

        if not path.is_file():
            raise FileNotFoundError(f"FakeLLM fixture not found: {path}")
        data = json.loads(path.read_text(encoding="utf-8"))
        responses = data.get("responses")
        if not isinstance(responses, list) or not responses:
            raise ValueError(f"Fixture {path} must contain a non-empty 'responses' list")
        return cls([str(r) if not isinstance(r, str) else r for r in responses], model_id=model_id)


def _approx_tokens(text: str) -> int:
    """A deliberately crude stand-in for a real tokenizer (~4 chars per
    token). Good enough to exercise the `RunMeta` fields and the cost
    back-of-envelope in Module 5 — not a claim about real token counts."""

    return max(1, len(text) // 4)
