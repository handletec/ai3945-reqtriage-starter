"""Tests for `FakeLLM` — SCAFFOLD ONLY. `reqtriage/llm/fake.py` doesn't
exist yet (see its TODO), so every test here is marked `xfail` and has
no real implementation. Writing these alongside your `FakeLLM` — not
after — is part of the exercise: it's what forces you to pin down
exactly what "replay a script" and "keep returning the last response"
mean before you accept a coding assistant's version of them.

Once you've implemented `FakeLLM`, come back here and:
  1. Fill in each test body with a real assertion (see the TODO in each
     one for what to check).
  2. Remove that test's `@pytest.mark.xfail` line.
  3. Add at least one negative case not listed below that you think
     matters (e.g. what should happen with a script containing a
     non-string item?).
"""

from __future__ import annotations

import pytest


@pytest.mark.xfail(reason="FakeLLM not implemented yet — see reqtriage/llm/fake.py", strict=False)
def test_from_script_replays_in_order():
    from reqtriage.llm.fake import FakeLLM

    # TODO: build FakeLLM(["first", "second"]), call .complete() twice,
    # assert the two calls return "first" then "second" in order.
    raise NotImplementedError


@pytest.mark.xfail(reason="FakeLLM not implemented yet — see reqtriage/llm/fake.py", strict=False)
def test_from_script_repeats_the_last_response_once_exhausted():
    from reqtriage.llm.fake import FakeLLM

    # TODO: build FakeLLM(["only"]), call .complete() three times,
    # assert every call returns "only" — never an exception, never
    # wrapping back to an earlier item.
    raise NotImplementedError


@pytest.mark.xfail(reason="FakeLLM not implemented yet — see reqtriage/llm/fake.py", strict=False)
def test_empty_script_is_rejected_at_construction_time():
    from reqtriage.llm.fake import FakeLLM

    # TODO: assert that FakeLLM([]) raises at construction time, not on
    # the first .complete() call.
    raise NotImplementedError


@pytest.mark.xfail(reason="FakeLLM not implemented yet — see reqtriage/llm/fake.py", strict=False)
def test_calls_are_recorded_for_test_assertions():
    from reqtriage.llm.fake import FakeLLM

    # TODO: call .complete(system=..., user=...) once, then assert the
    # instance recorded that (system, user) pair somewhere inspectable.
    raise NotImplementedError
