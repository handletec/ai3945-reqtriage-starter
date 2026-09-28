"""Typed contracts for the triage agent.

`TriageRequest` below is COMPLETE — it's the input schema, and you need
it to load the sample requests in `data/samples/`. Everything else is a
documented STUB: a class exists so other code can reference the name,
but its fields are not yet defined. Filling these in — as part of a
later, explicitly bounded exercise, not right now — is what turns "the
model can say anything" into "the model can only produce one of a small
number of well-defined shapes that Python then validates."

Do not fill in the stubs below on your own initiative. Each one belongs
to a specific later exercise:

* `TriageProposal` — the structured judgement the model will be trusted
  to propose (summary, category, priority, owner, confidence, ...).
  Needed once you're validating model output instead of just printing
  it raw.
* `AgentAction` — the two-shape envelope (`call_tool` / `final`) the
  model's raw JSON gets parsed into. Needed once the model can ask for a
  tool.
* `ToolCallRecord` — the audit record of one tool call attempt. Needed
  once there's a tool to call.
* `RunMeta` — run-level bookkeeping (model id, tool actions used, model
  turns used, timing). Needed once there's a bounded loop worth
  recording metadata about.
* `TriageResult` — the final, validated, participant-facing record,
  assembled from `TriageProposal` plus the Python-owned fields above.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class TriageRequest(BaseModel):
    """A single incoming engineering request, as it would arrive from a
    ticket form, an email alias, or a chat intake channel.

    This is untrusted *content* (the description is free text a human
    typed in a hurry) but a trusted *shape* — it is our own input
    schema, not something the model produced.
    """

    request_id: str = Field(min_length=1)
    source: str = Field(min_length=1)
    description: str
    reported_by: str | None = None
    submitted_at: str | None = None
    tags: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# STUBS — see this module's docstring. Do not implement these yet.
# ---------------------------------------------------------------------------


class TriageProposal(BaseModel):
    """STUB. The model's proposed triage judgement, once there is one.

    TODO (later exercise): fields for at least summary, category,
    priority, component, suggested_owner, related_known_issues,
    missing_info, confidence, needs_human_review, rationale. Think about
    which of these the model should be trusted to set directly, and
    which should only ever be set by deterministic Python policy — that
    distinction matters more than getting the field list exactly right
    on the first try.
    """


class AgentAction(BaseModel):
    """STUB. The envelope the model's raw JSON output gets parsed into.

    TODO (later exercise): this should end up as a discriminated union
    of exactly two shapes — "ask Python to run one bounded tool" and
    "here is my final proposal" — not a single model with every field
    optional. A single model with optional fields lets code accidentally
    read a field that doesn't apply to the action actually taken.
    """


class ToolCallRecord(BaseModel):
    """STUB. One row of the audit trail for a single tool call attempt.

    TODO (later exercise, once there is a tool to call): what happened,
    with what arguments, and how it ended — success, "not found" (not an
    error), or a genuine failure. Keep in mind: what the model sees back
    as data should probably NOT be the same shape as this audit record —
    a short summary for a human reading logs is a different job from the
    structured result the model needs to reason from.
    """


class RunMeta(BaseModel):
    """STUB. Run-level bookkeeping: model identity, timing, and — once
    there is a bounded agent loop — how much of its budget it used.

    TODO (later exercise): don't assume "number of loop iterations" is
    one number. A model that asks for a tool needs a turn to ask and a
    turn to finalise — those may need to be tracked and bounded
    separately from how many tool-action opportunities were spent.
    """


class TriageResult(BaseModel):
    """STUB. The final, validated, participant-facing record.

    TODO (later exercise): assembled from a validated `TriageProposal`
    plus `RunMeta` and the tool-call audit trail, plus a way to
    represent "this run could not produce a normal result" without
    crashing (an `error` field, not an exception escaping to the
    caller).
    """
