"""FakeLLM's own replay behaviour, tested in isolation from the agent.

Read `reqtriage/llm/fake.py`'s module docstring first: these tests prove
the REPLAY MECHANISM works, not that any response is a good one.
"""

from __future__ import annotations

import pytest

from reqtriage.llm.fake import FakeLLM, FakeLLMExhaustedError


def test_replays_responses_in_order():
    llm = FakeLLM.from_script(["one", "two", "three"])
    assert llm.complete("sys", "u1").text == "one"
    assert llm.complete("sys", "u2").text == "two"
    assert llm.complete("sys", "u3").text == "three"


def test_repeats_last_response_after_script_is_exhausted():
    llm = FakeLLM.from_script(["only"])
    assert llm.complete("sys", "u1").text == "only"
    assert llm.complete("sys", "u2").text == "only"
    assert llm.complete("sys", "u3").text == "only"


def test_records_every_call_for_test_assertions():
    llm = FakeLLM.from_script(["a"])
    llm.complete("system-text", "user-text")
    assert llm.calls == [("system-text", "user-text")]


def test_empty_script_is_rejected_at_construction():
    with pytest.raises(FakeLLMExhaustedError):
        FakeLLM.from_script([])


def test_from_fixture_file_loads_named_scenario(tmp_path):
    fixture = tmp_path / "scenario.json"
    fixture.write_text('{"responses": ["hello", "world"]}')
    llm = FakeLLM.from_fixture_file(fixture)
    assert llm.complete("s", "u").text == "hello"


def test_from_fixture_file_rejects_empty_responses_list(tmp_path):
    fixture = tmp_path / "scenario.json"
    fixture.write_text('{"responses": []}')
    with pytest.raises(ValueError):
        FakeLLM.from_fixture_file(fixture)


def test_from_fixture_file_raises_for_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        FakeLLM.from_fixture_file(tmp_path / "nope.json")
