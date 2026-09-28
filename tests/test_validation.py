"""The failure spine, tested directly: can we always turn arbitrary text
into either a valid AgentAction or a clearly-typed error, and can we
always build a valid TriageResult even when everything upstream failed?
"""

from __future__ import annotations

from reqtriage.models import CallToolAction, FinalAction, RunMeta
from reqtriage.validation import build_repair_prompt, degraded_result, extract_json, parse_action

VALID_FINAL_JSON = (
    '{"action": "final", "result": {"summary": "s", "missing_info": [], '
    '"confidence": 0.5, "needs_human_review": false, "rationale": "r"}}'
)


def test_extract_json_from_bare_object():
    assert extract_json('{"a": 1}') == '{"a": 1}'


def test_extract_json_strips_code_fence():
    text = "```json\n{\"a\": 1}\n```"
    assert extract_json(text) == '{"a": 1}'


def test_extract_json_strips_surrounding_prose():
    text = "Sure, here you go: " + VALID_FINAL_JSON + " Let me know if you need anything else."
    assert extract_json(text) == VALID_FINAL_JSON


def test_parse_action_succeeds_on_clean_json():
    action, error = parse_action(VALID_FINAL_JSON)
    assert error is None
    assert isinstance(action, FinalAction)


def test_parse_action_succeeds_on_fenced_json():
    action, error = parse_action("```json\n" + VALID_FINAL_JSON + "\n```")
    assert error is None
    assert isinstance(action, FinalAction)


def test_parse_action_succeeds_on_call_tool_shape():
    text = '{"action": "call_tool", "tool_name": "my_tool", "arguments": {"query": "x"}}'
    action, error = parse_action(text)
    assert error is None
    assert isinstance(action, CallToolAction)


def test_parse_action_reports_invalid_json():
    action, error = parse_action("{not: valid json at all")
    assert action is None
    assert error is not None
    assert error.kind == "invalid_json"


def test_parse_action_reports_invalid_schema_for_unknown_discriminator():
    action, error = parse_action('{"action": "do_something_sneaky"}')
    assert action is None
    assert error is not None
    assert error.kind == "invalid_schema"


def test_parse_action_reports_invalid_schema_for_missing_field():
    text = '{"action": "final", "result": {"summary": "s", "confidence": 0.5}}'
    action, error = parse_action(text)
    assert action is None
    assert error.kind == "invalid_schema"


def test_build_repair_prompt_includes_original_and_error_kind():
    action, error = parse_action("not json")
    prompt = build_repair_prompt("ORIGINAL PROMPT TEXT", error)
    assert "ORIGINAL PROMPT TEXT" in prompt
    assert "invalid_json" in prompt


def test_degraded_result_is_always_a_valid_triage_result_and_flags_review():
    meta = RunMeta(
        model_id="fake-llm-v1", prompt_version="v1-template", started_at="2026-01-01T00:00:00+00:00",
        duration_ms=1.0, tool_actions_used=1, model_turns_used=1, repair_used=False,
    )
    result = degraded_result(
        request_id="req_x", error_code="max_model_turns_exceeded", error_message="ran out of turns",
        tool_calls=[], meta=meta,
    )
    assert result.needs_human_review is True
    assert result.error == "max_model_turns_exceeded"
    assert result.confidence == 0.0
    assert result.missing_info == ["automated triage failed — manual review required"]


def test_degraded_result_honours_explicit_missing_info():
    meta = RunMeta(
        model_id="fake-llm-v1", prompt_version="v1-template", started_at="2026-01-01T00:00:00+00:00",
        duration_ms=1.0, tool_actions_used=0, model_turns_used=0, repair_used=False,
    )
    result = degraded_result(
        request_id="req_x", error_code="missing_description", error_message="request.description is empty",
        tool_calls=[], meta=meta, missing_info=["description"],
    )
    assert result.missing_info == ["description"]
