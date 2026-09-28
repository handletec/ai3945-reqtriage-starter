"""End-to-end tests for `run_triage` — the whole loop, with `FakeLLM`
standing in for the model. See `reqtriage/llm/fake.py` for why a fake and
not a mock, and what these tests do and do not prove.

CAPSTONE TEMPLATE: `TOOL_REGISTRY` is empty at this checkpoint (see
`reqtriage/tools/__init__.py`), so none of the tests below rely on a
real, registered tool — any tool name the model requests here is
deliberately unregistered, exercising the generic `unknown_tool` path.

TODO — once you register your own tool in `reqtriage/tools/__init__.py`,
add at minimum (per the course's mandatory capstone scope: one tool, one
positive case, one negative case):

  1. One end-to-end test where the model calls YOUR tool with valid
     arguments and the run finalises using the real (`status == "ok"`)
     result — your tool's positive case.
  2. One end-to-end test for your tool's negative case (a lookup that
     legitimately finds nothing, or invalid arguments) and confirms the
     run still completes / degrades safely rather than crashing.

Keep both anchored to a real registered tool name once one exists —
don't leave these as tests against `unknown_tool`.
"""

from __future__ import annotations

from reqtriage.agent import run_triage
from reqtriage.llm.base import LLMResponse
from reqtriage.llm.fake import FakeLLM, ScriptedResponse
from tests.conftest import fixture_path, load_sample


def _llm_for(scenario: str) -> FakeLLM:
    return FakeLLM.from_fixture_file(fixture_path(scenario))


# --- Happy path: pure L1 final-answer, no tool call ---


def test_happy_path_produces_validated_result_with_no_tool_call(settings):
    request = load_sample("example_001")
    llm = _llm_for("example")
    result = run_triage(request, llm, settings)

    assert result.error is None
    assert result.needs_human_review is False
    assert result.meta.model_turns_used == 1
    assert result.meta.tool_actions_used == 0
    assert len(llm.calls) == result.meta.model_turns_used  # every real invocation is a counted turn
    assert result.tool_calls == []


def test_negative_example_forces_human_review(settings):
    # example_002 / "example_negative" is scripted with low confidence and
    # missing_info populated — a legitimate negative case, not a crash.
    request = load_sample("example_002")
    llm = _llm_for("example_negative")
    result = run_triage(request, llm, settings)

    assert result.error is None
    assert result.needs_human_review is True
    assert result.missing_info != []


# --- Pre-check short-circuits before any model call ---


def test_missing_description_never_calls_the_model(make_request, settings):
    request = make_request(description="   ")
    llm = FakeLLM.from_script(["this would be a parse error if it were ever used"])
    result = run_triage(request, llm, settings)

    assert result.error == "missing_description"
    assert result.needs_human_review is True
    assert llm.calls == []  # the whole point of pre_check


def test_blocked_source_never_calls_the_model(make_request, settings):
    request = make_request(source="anonymous_form")
    llm = FakeLLM.from_script(["would also be unused"])
    result = run_triage(request, llm, settings)

    assert result.error == "blocked_source"
    assert llm.calls == []


# --- Unknown tool: the only "tool" path available at this checkpoint,
# since TOOL_REGISTRY is empty. This proves dispatch_tool's generic
# unknown-tool handling without needing a real registered tool. ---


def test_unknown_tool_request_consumes_the_action_budget_and_run_still_completes(make_settings, make_request):
    request = make_request(request_id="unknown-tool-test", description="Please look something up for me.")
    settings_budget = make_settings(max_tool_actions=1, max_model_turns=3)
    llm = FakeLLM.from_script(
        [
            '{"action": "call_tool", "tool_name": "some_tool_that_does_not_exist_yet", "arguments": {}}',
            '{"action": "final", "result": {"summary": "s", "missing_info": [], "confidence": 0.5, '
            '"needs_human_review": true, "rationale": "no tool was available, answering from the text alone"}}',
        ]
    )
    result = run_triage(request, llm, settings_budget)

    assert result.error is None
    assert result.meta.tool_actions_used == 1  # an unknown tool still spends the budget
    assert len(result.tool_calls) == 1
    assert result.tool_calls[0].status == "unknown_tool"


def test_unknown_tool_requests_do_not_bypass_the_action_budget(make_settings, make_request):
    request = make_request(request_id="unknown-tool-budget-test", description="Please look two things up.")
    settings_budget = make_settings(max_tool_actions=1, max_model_turns=3)
    llm = FakeLLM.from_script(
        [
            '{"action": "call_tool", "tool_name": "not_registered", "arguments": {}}',
            '{"action": "call_tool", "tool_name": "not_registered", "arguments": {}}',
            '{"action": "final", "result": {"summary": "s", "missing_info": [], "confidence": 0.5, '
            '"needs_human_review": true, "rationale": "r"}}',
        ]
    )
    result = run_triage(request, llm, settings_budget)

    assert result.error is None
    assert result.meta.tool_actions_used == 1
    assert len(result.tool_calls) == 2
    assert result.tool_calls[0].status == "unknown_tool"
    # The second identical request is refused by the budget, not
    # re-dispatched — an unknown tool name does not bypass the limit.
    assert result.tool_calls[1].status == "action_limit_reached"


# --- max_model_turns: the independent safety bound ---


def test_max_model_turns_terminates_a_model_that_never_finalises(make_settings, make_request):
    # max_tool_actions is deliberately set HIGHER than max_model_turns, so
    # this test proves the INDEPENDENT model-turn safety bound is what
    # stops the run — not the action budget (which is never exhausted).
    request = make_request(request_id="never-final-test", description="Keeps asking for a tool forever.")
    settings_small_turns = make_settings(max_tool_actions=5, max_model_turns=2)
    llm = FakeLLM.from_script(
        ['{"action": "call_tool", "tool_name": "not_registered", "arguments": {}}']
    )  # last item repeats forever — see FakeLLM's replay model
    result = run_triage(request, llm, settings_small_turns)

    assert result.error == "max_model_turns_exceeded"
    assert result.needs_human_review is True
    assert result.meta.model_turns_used == 2
    assert len(llm.calls) == 2  # the run can never make more real model calls than max_model_turns allows
    assert result.meta.tool_actions_used == 2  # both turns spent a real action; the budget wasn't the limiter


# --- Model-invocation accounting: EVERY llm.complete() call is a turn,
# and RunMeta's token totals sum usage across ALL of them (normal turns
# and the repair call alike). ---


def test_single_model_call_reports_one_turn_and_its_exact_usage(make_settings, make_request):
    request = make_request(request_id="single-call-usage-test")
    settings_l1 = make_settings(max_tool_actions=0, max_model_turns=2)
    llm = FakeLLM.from_script(
        [
            ScriptedResponse(
                '{"action": "final", "result": {"summary": "s", "missing_info": [], "confidence": 0.6, '
                '"needs_human_review": false, "rationale": "r"}}',
                prompt_tokens=120,
                completion_tokens=30,
            )
        ]
    )
    result = run_triage(request, llm, settings_l1)

    assert result.error is None
    assert result.meta.model_turns_used == 1
    assert len(llm.calls) == 1
    assert result.meta.prompt_tokens == 120
    assert result.meta.completion_tokens == 30
    assert result.meta.prompt_tokens_unreported_calls == 0
    assert result.meta.completion_tokens_unreported_calls == 0


def test_multi_turn_run_sums_usage_across_every_model_call(make_settings, make_request):
    request = make_request(request_id="multi-call-usage-test")
    settings_budget = make_settings(max_tool_actions=1, max_model_turns=3)
    llm = FakeLLM.from_script(
        [
            ScriptedResponse(
                '{"action": "call_tool", "tool_name": "not_registered", "arguments": {}}',
                prompt_tokens=100,
                completion_tokens=20,
            ),
            ScriptedResponse(
                '{"action": "final", "result": {"summary": "s", "missing_info": [], "confidence": 0.6, '
                '"needs_human_review": true, "rationale": "r"}}',
                prompt_tokens=200,
                completion_tokens=40,
            ),
        ]
    )
    result = run_triage(request, llm, settings_budget)

    assert result.error is None
    assert result.meta.model_turns_used == 2
    assert len(llm.calls) == 2
    assert result.meta.prompt_tokens == 100 + 200
    assert result.meta.completion_tokens == 20 + 40
    assert result.meta.prompt_tokens_unreported_calls == 0
    assert result.meta.completion_tokens_unreported_calls == 0


def test_partial_usage_is_labelled_with_unreported_call_count(make_settings, make_request):
    request = make_request(request_id="partial-usage-test")
    settings_budget = make_settings(max_tool_actions=1, max_model_turns=3)
    llm = FakeLLM.from_script(
        [
            ScriptedResponse(
                '{"action": "call_tool", "tool_name": "not_registered", "arguments": {}}',
                prompt_tokens=None,
                completion_tokens=None,
            ),
            ScriptedResponse(
                '{"action": "final", "result": {"summary": "s", "missing_info": [], "confidence": 0.6, '
                '"needs_human_review": true, "rationale": "r"}}',
                prompt_tokens=42,
                completion_tokens=17,
            ),
        ]
    )
    result = run_triage(request, llm, settings_budget)

    assert result.error is None
    assert result.meta.model_turns_used == 2
    assert result.meta.prompt_tokens == 42
    assert result.meta.completion_tokens == 17
    assert result.meta.prompt_tokens_unreported_calls == 1
    assert result.meta.completion_tokens_unreported_calls == 1


def test_repair_call_is_counted_as_a_model_turn_and_its_usage_is_included(settings, make_request):
    # Defect fix: the repair call is a real llm.complete() invocation
    # like any other. It must consume a model turn AND its usage must
    # be added to the run total — not silently excluded because it
    # happened inside the "repair" branch rather than the main loop.
    request = make_request(request_id="repair-usage-test")
    llm = FakeLLM.from_script(
        [
            ScriptedResponse("not json at all — the original, unusable response", prompt_tokens=80, completion_tokens=10),
            ScriptedResponse(
                '{"action": "final", "result": {"summary": "s", "missing_info": [], "confidence": 0.6, '
                '"needs_human_review": false, "rationale": "r"}}',
                prompt_tokens=95,
                completion_tokens=22,
            ),
        ]
    )
    result = run_triage(request, llm, settings)

    assert result.error is None
    assert result.meta.repair_used is True
    assert result.meta.model_turns_used == 2
    assert len(llm.calls) == 2
    assert result.meta.prompt_tokens == 80 + 95
    assert result.meta.completion_tokens == 10 + 22


def test_repair_not_attempted_when_no_model_turn_budget_remains(make_settings, make_request):
    # Defect fix: the repair attempt must obey max_model_turns exactly
    # like every other call. With the budget already spent on the
    # original (malformed) call, the repair call must NEVER be made —
    # proven here by a poisoned second script item whose absurd token
    # counts would show up in the totals if it were ever reached.
    request = make_request(request_id="repair-no-budget-test")
    settings_no_budget = make_settings(max_tool_actions=0, max_model_turns=1)
    llm = FakeLLM.from_script(
        [
            ScriptedResponse("not json at all", prompt_tokens=80, completion_tokens=10),
            ScriptedResponse("must never be reached", prompt_tokens=999, completion_tokens=999),
        ]
    )
    result = run_triage(request, llm, settings_no_budget)

    assert result.error == "max_model_turns_exceeded"
    assert result.needs_human_review is True
    assert result.meta.repair_used is False  # no repair call was actually made
    assert result.meta.model_turns_used == 1
    assert len(llm.calls) == 1  # the repair call must never have been attempted
    assert result.meta.prompt_tokens == 80
    assert result.meta.completion_tokens == 10


def test_missing_token_usage_is_never_invented(make_settings, make_request):
    # If no invocation this run ever reports a token count, the run
    # total must be None — never a fabricated 0.
    request = make_request(request_id="no-usage-test")
    settings_l1 = make_settings(max_tool_actions=0, max_model_turns=2)
    llm = FakeLLM.from_script(
        [
            ScriptedResponse(
                '{"action": "final", "result": {"summary": "s", "missing_info": [], "confidence": 0.6, '
                '"needs_human_review": false, "rationale": "r"}}',
                prompt_tokens=None,
                completion_tokens=None,
            )
        ]
    )
    result = run_triage(request, llm, settings_l1)

    assert result.error is None
    assert result.meta.model_turns_used == 1
    assert result.meta.prompt_tokens is None
    assert result.meta.completion_tokens is None
    assert result.meta.prompt_tokens_unreported_calls == 1
    assert result.meta.completion_tokens_unreported_calls == 1


# --- Repair: exactly one attempt, and it can succeed ---


def test_repair_recovers_from_one_malformed_response(settings, make_request):
    request = make_request(request_id="repair-success-test")
    llm = FakeLLM.from_script(
        [
            "not json at all, the model rambled instead",
            '{"action": "final", "result": {"summary": "s", "missing_info": [], "confidence": 0.7, '
            '"needs_human_review": false, "rationale": "recovered after repair"}}',
        ]
    )
    result = run_triage(request, llm, settings)

    assert result.error is None
    assert result.meta.repair_used is True
    assert result.rationale == "recovered after repair"


def test_repair_budget_is_exactly_one_call_then_gives_up(settings, make_request):
    request = make_request(request_id="repair-budget-test")
    llm = FakeLLM.from_script(
        [
            "not json at all, first attempt",
            "still not json, second attempt",
        ]
    )
    result = run_triage(request, llm, settings)

    assert result.error is not None
    assert result.error.startswith("invalid_action_")
    assert result.meta.repair_used is True
    assert len(llm.calls) == 2  # original + exactly one repair, never more


# --- Tool-level misbehaviour inside the loop does not crash the run ---


def test_invalid_action_after_repair_gives_up_and_degrades_safely(settings, make_request):
    request = make_request(request_id="bad-action-test")
    llm = FakeLLM.from_script(
        [
            '{"action": "do_something_sneaky"}',
            '{"action": "still_not_a_real_action"}',
        ]
    )
    result = run_triage(request, llm, settings)

    assert result.error is not None
    assert result.error.startswith("invalid_action_")
    assert result.needs_human_review is True


# --- A genuine infrastructure failure degrades safely instead of crashing ---


class _AlwaysFailsLLM:
    model_id = "broken-llm"

    def complete(self, system: str, user: str) -> LLMResponse:
        raise RuntimeError("simulated connection timeout")


def test_llm_infrastructure_failure_degrades_safely(settings, make_request):
    request = make_request(request_id="infra-failure-test")
    result = run_triage(request, _AlwaysFailsLLM(), settings)

    assert result.error == "llm_call_failed"
    assert result.needs_human_review is True
    assert "simulated connection timeout" in result.rationale
    assert result.meta.model_turns_used == 1
    assert result.meta.prompt_tokens is None
    assert result.meta.completion_tokens is None
    assert result.meta.prompt_tokens_unreported_calls == 1
    assert result.meta.completion_tokens_unreported_calls == 1


# --- Deterministic policy still wins even when the model tries otherwise ---


def test_confidence_threshold_override_end_to_end(settings, make_request):
    request = make_request(request_id="confidence-override-test")
    llm = FakeLLM.from_script(
        [
            '{"action": "final", "result": {"summary": "s", "missing_info": [], "confidence": 0.05, '
            '"needs_human_review": false, "rationale": "the model itself was confident enough"}}'
        ]
    )
    result = run_triage(request, llm, settings)

    assert result.error is None
    # The model proposed needs_human_review=False, but confidence is well
    # below the configured threshold — post_process must override it.
    assert result.needs_human_review is True
