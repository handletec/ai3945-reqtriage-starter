"""Typed contracts for the agent.

CAPSTONE TEMPLATE. Everything in this file except `TriageProposal` and
`TriageResult` is generic mechanism, carried over unchanged from the
reference build — you shouldn't need to touch `TriageRequest`,
`CallToolAction`/`FinalAction`/`AgentAction`, `ToolCallRecord`, or
`RunMeta` just to adapt this to a new task.

`TriageProposal` and `TriageResult` below have been reduced to the
handful of fields that make sense for ANY triage-shaped agent
(a summary, a confidence score, a human-review flag, a rationale, what's
missing). TODO: add the fields specific to YOUR task — the equivalents
of "category", "priority", "component", "suggested_owner" from the
reqtriage reference build, whatever those are for your domain — and
keep `docs/brief.md`'s "Outputs" section in sync with whatever you add.

Field ownership (read this before editing anything else in the package):

* `TriageRequest`  — comes from the caller (a JSON file on disk in this
  course). Never produced by the model. Generic; you probably don't
  need to change its shape, though nothing stops you.
* `TriageProposal` — the ONLY thing the model is trusted to produce. It
  is a *proposal*, not the final record: `rules.post_process` may
  downgrade or strip fields in it before it becomes a `TriageResult`.
* `ToolCallRecord` — built exclusively by Python (`agent.py` /
  `reqtriage/tools`). The model never writes one directly; it only ever
  sees a summary of one fed back as data. Generic.
* `RunMeta`         — built exclusively by Python. Model identity, prompt
  version, timing and token counts are runtime facts, not something an
  untrusted model call gets to assert about itself. Generic.
* `TriageResult`    — the final, validated, participant-facing record.
  Assembled by `agent.py` from a `TriageProposal` plus the Python-owned
  fields above.
* `AgentAction`     — the ONLY shape the model's raw JSON output is ever
  parsed into. It is a discriminated union of exactly two members:
  `call_tool` (ask Python to run one allowed lookup) and `final` (propose
  a finished `TriageProposal`). This is what makes the autonomy level
  legible in code: the number of `call_tool` action opportunities the
  model may spend is a separate, explicit budget
  (`settings.agent.max_tool_actions`) from the number of times the model
  gets to speak at all (`settings.agent.max_model_turns`). A request
  spends an action opportunity once it passes the budget check and enters
  dispatch, even when dispatch rejects the tool name/arguments or reports
  a tool failure. L1 sets the
  action budget to 0, L2 to 1, L3 to a small number greater than 1. See
  `agent.py` for where that distinction lives — it is not simply "loop N
  times". Generic; do not rename the two action shapes.
"""

from __future__ import annotations

from typing import Annotated, Any, Literal, Union

from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Shared enums
# ---------------------------------------------------------------------------

# TODO: add your own domain enums here (the reqtriage reference build had
# Category and Priority) once TriageProposal/TriageResult need them.

ToolStatus = Literal[
    "ok",
    "not_found",
    "invalid_arguments",
    "unknown_tool",
    "error",
    # The model asked for a tool it was otherwise allowed to use, but the
    # run had already spent its `max_tool_actions` budget. The tool is
    # NEVER executed in this case — see agent.py. This status exists so
    # the refusal is visible in the audit trail, exactly like any other
    # outcome, rather than being silently dropped.
    "action_limit_reached",
]


# ---------------------------------------------------------------------------
# Input — generic, carried over unchanged
# ---------------------------------------------------------------------------


class TriageRequest(BaseModel):
    """A single incoming request, as it would arrive from a ticket form,
    an email alias, or a chat intake channel.

    This is untrusted *content* (the description is free text a human
    typed in a hurry) but a trusted *shape* — it is our own input schema,
    not something the model produced.
    """

    request_id: str = Field(min_length=1)
    source: str = Field(min_length=1)
    description: str
    reported_by: str | None = None
    submitted_at: str | None = None
    tags: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# What the model is trusted to propose — TEMPLATE, minimal generic fields
# ---------------------------------------------------------------------------


class TriageProposal(BaseModel):
    """The model's proposed judgement.

    This is the *only* pydantic model the model's output is ever allowed
    to populate. Everything in it is a proposal: `rules.post_process` is
    free to downgrade or strip fields before it becomes a `TriageResult`.

    TEMPLATE: only the fields every triage-shaped agent needs are here.
    Add your task's domain-specific fields (whatever your equivalent of
    category/priority/owner is), and update `reqtriage/prompts.py` and
    `reqtriage/rules.py::post_process` to match.
    """

    summary: str = Field(max_length=200)
    missing_info: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)
    needs_human_review: bool
    rationale: str = Field(max_length=400)


# ---------------------------------------------------------------------------
# The bounded action the model is allowed to choose at each step — generic
# ---------------------------------------------------------------------------


class CallToolAction(BaseModel):
    """"Run one allowed lookup and give me the result." Never executes
    anything itself — `agent.py` validates `tool_name` against the
    registry allow-list before dispatching."""

    action: Literal["call_tool"] = "call_tool"
    tool_name: str
    arguments: dict[str, Any] = Field(default_factory=dict)


class FinalAction(BaseModel):
    """"I'm done — here is my proposed result." Ends the loop."""

    action: Literal["final"] = "final"
    result: TriageProposal


# A discriminated union keyed on the `action` field. This is the entire
# vocabulary the model is allowed to speak in: exactly these two shapes,
# nothing else. `reqtriage.validation.parse_action` is the only place raw
# model text is turned into one of these.
AgentAction = Annotated[Union[CallToolAction, FinalAction], Field(discriminator="action")]


# ---------------------------------------------------------------------------
# Python-owned record keeping — generic, carried over unchanged
# ---------------------------------------------------------------------------


class ToolCallRecord(BaseModel):
    """One row of the AUDIT trail — a concise record of what was
    attempted, for `TriageResult.tool_calls`, `logs/runs.jsonl`, and
    diagnosis. Built only by `reqtriage.tools.dispatch_tool` (or, for a
    refused over-budget attempt, by `agent.py` itself).

    This is deliberately NOT what the model sees back as data — it may
    carry only a short `result_summary` (an identifier or count), never
    the tool's full structured result. The model instead receives the
    narrow result built by `reqtriage.tools.describe_result_for_model`.
    Conflating the two was a real bug in an earlier version of the
    reference build: the model was reasoning from `result_summary`
    strings that did not contain enough detail to justify what it then
    said. Keep them separate in your own tool too.
    """

    step: int = Field(ge=1)
    tool_name: str
    arguments: dict[str, Any]
    status: ToolStatus
    result_summary: str | None = None
    error: str | None = None
    duration_ms: float = Field(ge=0.0)


class RunMeta(BaseModel):
    """Runtime facts about how this result was produced. Populated
    entirely by `agent.py` after the run completes — never by the model.

    `tool_actions_used` and `model_turns_used` are deliberately two
    different numbers (see `agent.py`). A `call_tool` request that
    reaches dispatch while budget remains spends an action opportunity,
    even if it is unknown/invalid or the tool fails. Once the action
    budget is already spent, later `call_tool` requests are refused
    without dispatch; those refusals can still consume model turns.
    Keeping the counters separate makes that distinction visible.

    `model_turns_used` counts EVERY real `llm.complete()` invocation made
    during the run, with no exceptions — this includes the one
    validation-repair call when it happens.

    `prompt_tokens` / `completion_tokens` sum the values that were
    actually reported. `None` means no invocation reported that field.
    The matching `*_unreported_calls` counter records how many completed
    model responses omitted that usage field. Therefore a numeric sum
    with a non-zero unreported-call count is explicitly partial / a
    lower bound, not a complete run total.
    """

    model_id: str
    prompt_version: str
    started_at: str  # ISO-8601 UTC
    duration_ms: float = Field(ge=0.0)
    tool_actions_used: int = Field(ge=0)
    model_turns_used: int = Field(ge=0)
    repair_used: bool
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    prompt_tokens_unreported_calls: int = Field(default=0, ge=0)
    completion_tokens_unreported_calls: int = Field(default=0, ge=0)


# ---------------------------------------------------------------------------
# Final output — TEMPLATE, minimal generic fields
# ---------------------------------------------------------------------------


class TriageResult(BaseModel):
    """The final, validated record. This is what `python -m reqtriage`
    prints and what `logs/runs.jsonl` summarises.

    `error` is `None` for a normal result. It is set to a short error
    code (see `reqtriage.validation`) when the record is a *safe degraded
    output* produced after the model or a tool misbehaved — in that case
    `needs_human_review` is always `True`.

    TEMPLATE: keep this in sync field-for-field with `TriageProposal`
    above, plus the Python-owned fields (`tool_calls`, `meta`, `error`).
    """

    request_id: str
    summary: str = Field(max_length=200)
    missing_info: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)
    needs_human_review: bool
    rationale: str = Field(max_length=400)
    tool_calls: list[ToolCallRecord] = Field(default_factory=list)
    meta: RunMeta
    error: str | None = None
