"""FakeLLM — YOUR FIRST EXERCISE. Not implemented yet.

Why a fake at all: this course runs with no network access and no
credentials, for every practical and every test. A `FakeLLM` is a
hand-written, deterministic stand-in for a real model that replays a
scripted sequence of raw text responses — one per call to `.complete()`.

Why hand-written rather than a mocking library: the fake's whole job is
to let you (and later, a course participant reviewing your code) open,
read, and edit a realistic scripted model response like any other data
file — a plain JSON fixture, not something hidden behind test-framework
machinery.

## What to build

Give a coding assistant a bounded engineering task rather than asking it
to "add FakeLLM" in the abstract. A reasonable ask:

    "Implement FakeLLM in reqtriage/llm/fake.py so it satisfies the
    LLMClient protocol in reqtriage/llm/base.py. Requirements:
    - Constructed from an ordered list of raw response strings (a
      'script'). `FakeLLM(["resp1", "resp2"])`.
    - Each call to `.complete(system, user)` returns the next scripted
      response as an `LLMResponse`, in order.
    - Once the script is exhausted, keep returning the LAST response
      (never raise, never wrap around to the first).
    - Raise a clear error at CONSTRUCTION time if the script is empty —
      that's an authoring mistake, not a runtime condition to handle
      lazily.
    - Record every (system, user) pair passed to `.complete()` on the
      instance, so a test can assert on what was actually sent.
    - Add a classmethod to build one from a JSON fixture file shaped
      like `{"responses": ["...", "..."]}`, for named, reusable
      scenarios rather than inline scripts everywhere."

## Review this before you accept it

- Does `.complete()` actually implement `LLMClient` from
  `reqtriage/llm/base.py` — same method name, same signature, same
  return type? A subtly different signature will pass a casual read and
  fail the first time something else calls it polymorphically.
- What happens on the call AFTER the script runs out? Read the code, not
  just the docstring the assistant wrote — try it with a one-item script
  and three calls before you trust it.
- Does anything here touch the network, read `.env`, or import a real
  provider SDK? It shouldn't — a fake has no reason to.
- Is `LLMResponse.text` used anywhere as if it were already validated or
  structured (parsed as JSON, indexed into fields)? It shouldn't be —
  that's not this file's job.

## Validate it

Once you've written (or accepted) an implementation, run
`python -m pytest tests/test_fake_llm.py -v`. It's a mostly-empty
scaffold right now with a few TODOs — filling those in with your own
assertions, based on the requirements above, is part of the exercise:
writing the test alongside the code is what makes you actually specify
the "keep returning the last response" behaviour instead of assuming a
coding assistant got it right.
"""

from __future__ import annotations

# TODO: implement FakeLLM here, satisfying reqtriage.llm.base.LLMClient.
#
# from reqtriage.llm.base import LLMResponse
#
# class FakeLLM:
#     def __init__(self, script: list[str], model_id: str = "fake-llm-v1") -> None:
#         ...
#
#     def complete(self, system: str, user: str) -> LLMResponse:
#         ...
#
#     @classmethod
#     def from_fixture_file(cls, path, model_id: str = "fake-llm-v1") -> "FakeLLM":
#         ...
