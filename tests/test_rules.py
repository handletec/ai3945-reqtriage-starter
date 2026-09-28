"""Policy tests: everything the architecture says must never depend on
the model, tested with no model in the loop at all.

CAPSTONE TEMPLATE: `post_process` at this checkpoint implements exactly
one generic rule (a confidence floor). TODO: once you add your own
domain-specific rules to `reqtriage/rules.py::post_process` (a keyword
floor, a provenance check against your tool's results, ...), add tests
for them here following the same pattern.
"""

from __future__ import annotations

from reqtriage.models import TriageProposal
from reqtriage.rules import post_process, pre_check


def _proposal(**overrides) -> TriageProposal:
    base = dict(
        summary="s",
        missing_info=[],
        confidence=0.8,
        needs_human_review=False,
        rationale="r",
    )
    base.update(overrides)
    return TriageProposal.model_validate(base)


# --- pre_check ---


def test_pre_check_rejects_empty_description(make_request, settings):
    request = make_request(description="   ")
    failure = pre_check(request, settings)
    assert failure is not None
    assert failure.code == "missing_description"


def test_pre_check_rejects_blocked_source(make_request, settings):
    request = make_request(source="anonymous_form")
    failure = pre_check(request, settings)
    assert failure is not None
    assert failure.code == "blocked_source"


def test_pre_check_passes_normal_request(make_request, settings):
    request = make_request(source="ticket_form", description="A real problem.")
    assert pre_check(request, settings) is None


# --- post_process: confidence threshold ---


def test_low_confidence_forces_human_review(make_request, settings):
    request = make_request()
    proposal = _proposal(confidence=0.1, needs_human_review=False)
    adjusted = post_process(request, proposal, [], settings)
    assert adjusted.needs_human_review is True


def test_confidence_exactly_at_threshold_does_not_force_review(make_request, settings):
    request = make_request()
    proposal = _proposal(confidence=settings.policy.confidence_threshold, needs_human_review=False)
    adjusted = post_process(request, proposal, [], settings)
    assert adjusted.needs_human_review is False


def test_high_confidence_does_not_force_review_by_itself(make_request, settings):
    request = make_request(description="A perfectly ordinary request.")
    proposal = _proposal(confidence=0.95, needs_human_review=False)
    adjusted = post_process(request, proposal, [], settings)
    assert adjusted.needs_human_review is False


def test_model_requested_review_survives_even_with_high_confidence(make_request, settings):
    # post_process only ever tightens, never loosens: if the model itself
    # asked for human review, that must never be cleared by this rule.
    request = make_request()
    proposal = _proposal(confidence=0.99, needs_human_review=True)
    adjusted = post_process(request, proposal, [], settings)
    assert adjusted.needs_human_review is True
