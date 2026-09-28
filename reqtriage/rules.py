"""Deterministic policy: everything the architecture says must NEVER
depend on the model.

CAPSTONE TEMPLATE. The mechanism — two entry points, called from
`agent.py`, neither of which ever calls the model — is generic and
worth keeping exactly as-is. The BODY of each function below is a
minimal, generic placeholder; you're expected to replace it with your
own task's policy.

* `pre_check()`  — runs BEFORE the model is ever called. A request that
  fails here never reaches the LLM boundary at all.
* `post_process()` — runs AFTER the model has produced a `FinalAction`,
  and is the only place fields are allowed to be overridden. This is the
  concrete enforcement of "the model proposes, Python decides":
  everything here should be plain, testable, keyword/lookup-table logic
  with no model call in it.

TODO: once you have a tool, add a provenance check here in
`post_process()` — the reqtriage reference build's version stripped any
`suggested_owner` that wasn't actually confirmed by a `lookup_owner`
tool result that run, and forced `needs_human_review=True` when it did.
Whatever your tool returns, the same principle applies: a field the
model claims your tool confirmed should only survive if a tool call
this run actually returned it.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from reqtriage.config import Settings
from reqtriage.models import ToolCallRecord, TriageProposal, TriageRequest


@dataclass(frozen=True)
class PreCheckFailure:
    """Why a request was rejected before ever reaching the model."""

    code: str
    message: str
    missing_info: list[str] = field(default_factory=list)


def pre_check(request: TriageRequest, settings: Settings) -> PreCheckFailure | None:
    """Return a `PreCheckFailure` if this request must not go to the
    model at all, else `None` to proceed.

    The two checks below (empty description, disallowed source) are
    generic enough to keep as-is. Add your own task-specific pre-checks
    here — anything you can reject deterministically before spending a
    model call should go here, not in a prompt instruction hoping the
    model notices.
    """

    if not request.description or not request.description.strip():
        return PreCheckFailure(
            code="missing_description",
            message="request.description is empty",
            missing_info=["description"],
        )

    if request.source not in settings.policy.allowed_sources:
        return PreCheckFailure(
            code="blocked_source",
            message=(
                f"source '{request.source}' is not in the allowed list "
                f"{list(settings.policy.allowed_sources)}"
            ),
        )

    return None


def post_process(
    request: TriageRequest,
    proposal: TriageProposal,
    tool_results: list[tuple[ToolCallRecord, Any]],
    settings: Settings,
) -> TriageProposal:
    """Apply every deterministic post-rule to the model's proposal and
    return an adjusted `TriageProposal`. Never calls the model. Never
    raises for a normal policy adjustment — only ever tightens the
    proposal, never loosens it.

    Only one generic rule is implemented here: low confidence always
    forces human review. TODO: add your own task's rules — a priority
    floor for urgent keywords, provenance checks for anything your tool
    returns, whatever your domain needs. Model each new rule as its own
    clearly-commented block, the way the reqtriage reference build did,
    so a reviewer can see which rule did what to the proposal.
    """

    needs_human_review = proposal.needs_human_review
    missing_info = list(proposal.missing_info)

    # --- Low confidence always goes to a human, regardless of the rest. ---
    if proposal.confidence < settings.policy.confidence_threshold:
        needs_human_review = True

    return proposal.model_copy(
        update={
            "needs_human_review": needs_human_review,
            "missing_info": missing_info,
        }
    )
