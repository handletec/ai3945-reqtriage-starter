"""Schema-level tests: does the contract itself reject what it should?

These deliberately do not touch the agent loop — they exist so that a
schema mistake (wrong bound, wrong discriminator) is caught in
milliseconds, not by chasing it through a full end-to-end run.

CAPSTONE TEMPLATE: only the 5 generic `TriageProposal`/`TriageResult`
fields are tested here (`summary`, `missing_info`, `confidence`,
`needs_human_review`, `rationale`) — there is no `category`/`priority`/
`component`/`suggested_owner`/`related_known_issues` at this checkpoint.
Once you add your own domain fields, add matching validation tests here.
"""

from __future__ import annotations

import pytest
from pydantic import TypeAdapter, ValidationError

from reqtriage.models import (
    AgentAction,
    CallToolAction,
    FinalAction,
    RunMeta,
    ToolCallRecord,
    TriageProposal,
    TriageRequest,
    TriageResult,
)

ACTION_ADAPTER = TypeAdapter(AgentAction)


def _valid_proposal(**overrides) -> dict:
    base = dict(
        summary="A short summary",
        missing_info=[],
        confidence=0.5,
        needs_human_review=False,
        rationale="A short rationale",
    )
    base.update(overrides)
    return base


def test_triage_request_requires_non_empty_ids():
    with pytest.raises(ValidationError):
        TriageRequest.model_validate({"request_id": "", "source": "ticket_form", "description": "x"})


def test_triage_request_accepts_minimal_shape():
    request = TriageRequest.model_validate(
        {"request_id": "r1", "source": "ticket_form", "description": "x"}
    )
    assert request.reported_by is None
    assert request.submitted_at is None
    assert request.tags == []


@pytest.mark.parametrize("confidence", [-0.1, 1.1])
def test_triage_proposal_confidence_must_be_in_unit_interval(confidence):
    with pytest.raises(ValidationError):
        TriageProposal.model_validate(_valid_proposal(confidence=confidence))


def test_triage_proposal_summary_length_is_bounded():
    with pytest.raises(ValidationError):
        TriageProposal.model_validate(_valid_proposal(summary="x" * 201))


def test_triage_proposal_rationale_length_is_bounded():
    with pytest.raises(ValidationError):
        TriageProposal.model_validate(_valid_proposal(rationale="x" * 401))


def test_triage_proposal_requires_needs_human_review():
    with pytest.raises(ValidationError):
        TriageProposal.model_validate(
            {"summary": "s", "missing_info": [], "confidence": 0.5, "rationale": "r"}
        )


def test_agent_action_discriminates_call_tool():
    action = ACTION_ADAPTER.validate_python(
        {"action": "call_tool", "tool_name": "my_tool", "arguments": {"query": "x"}}
    )
    assert isinstance(action, CallToolAction)
    assert action.tool_name == "my_tool"


def test_agent_action_discriminates_final():
    action = ACTION_ADAPTER.validate_python({"action": "final", "result": _valid_proposal()})
    assert isinstance(action, FinalAction)
    assert action.result.summary == "A short summary"


def test_agent_action_rejects_unknown_discriminator():
    with pytest.raises(ValidationError):
        ACTION_ADAPTER.validate_python({"action": "do_something_else"})


def test_agent_action_rejects_missing_required_field():
    with pytest.raises(ValidationError):
        ACTION_ADAPTER.validate_python({"action": "call_tool"})  # missing tool_name


def test_triage_result_requires_meta():
    with pytest.raises(ValidationError):
        TriageResult.model_validate(
            {
                "request_id": "r1",
                "summary": "s",
                "confidence": 0.5,
                "needs_human_review": False,
                "rationale": "r",
            }
        )


def test_tool_call_record_status_is_constrained():
    with pytest.raises(ValidationError):
        ToolCallRecord.model_validate(
            {
                "step": 1,
                "tool_name": "my_tool",
                "arguments": {},
                "status": "totally_fine_probably",
                "duration_ms": 1.0,
            }
        )


def test_tool_call_record_accepts_every_declared_status():
    for status in ("ok", "not_found", "invalid_arguments", "unknown_tool", "error", "action_limit_reached"):
        record = ToolCallRecord.model_validate(
            {
                "step": 1,
                "tool_name": "my_tool",
                "arguments": {},
                "status": status,
                "duration_ms": 1.0,
            }
        )
        assert record.status == status


def test_run_meta_rejects_negative_duration():
    with pytest.raises(ValidationError):
        RunMeta.model_validate(
            {
                "model_id": "fake-llm-v1",
                "prompt_version": "v1-template",
                "started_at": "2026-01-01T00:00:00+00:00",
                "duration_ms": -1.0,
                "tool_actions_used": 1,
                "model_turns_used": 1,
                "repair_used": False,
            }
        )


def test_run_meta_allows_missing_token_counts():
    meta = RunMeta.model_validate(
        {
            "model_id": "fake-llm-v1",
            "prompt_version": "v1-template",
            "started_at": "2026-01-01T00:00:00+00:00",
            "duration_ms": 1.0,
            "tool_actions_used": 0,
            "model_turns_used": 1,
            "repair_used": False,
        }
    )
    assert meta.prompt_tokens is None
    assert meta.completion_tokens is None
