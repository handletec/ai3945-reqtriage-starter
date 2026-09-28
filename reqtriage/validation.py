"""The failure spine: turning untrusted model text into a validated
`AgentAction`, and producing a safe degraded `TriageResult` whenever that
is not possible.

Every failure mode this module handles is real and gets exercised in
`tests/test_validation.py`:

* the model wraps its JSON in prose or a code fence
* the model returns JSON that is syntactically invalid
* the model returns JSON that is syntactically valid but does not match
  either `CallToolAction` or `FinalAction` (wrong discriminator, missing
  field, wrong type, wrong enum value)

`agent.py` is the only caller of `parse_action`. It is allowed exactly
ONE repair attempt per run (see `RepairBudget`) — never an unbounded
retry loop.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass

from pydantic import TypeAdapter, ValidationError

from reqtriage.models import AgentAction, RunMeta, ToolCallRecord, TriageResult

_ACTION_ADAPTER: TypeAdapter = TypeAdapter(AgentAction)

_FENCE_RE = re.compile(r"```(?:json)?\s*(.*?)```", re.DOTALL | re.IGNORECASE)


@dataclass(frozen=True)
class ActionError:
    """What went wrong trying to turn raw model text into an `AgentAction`.
    Deliberately a plain typed value, not an exception — `agent.py` reads
    `.kind`/`.message` to decide whether a repair attempt is worthwhile
    and what to tell the model."""

    kind: str  # "invalid_json" | "invalid_schema"
    message: str
    raw_text: str


def extract_json(text: str) -> str:
    """Defensively pull a JSON object out of raw model text.

    Handles the shapes real models actually produce: a fenced ```json
    block, a bare JSON object, or a JSON object preceded/followed by
    prose ("Here is my answer: {...} Let me know if..."). Does NOT
    attempt to fix broken JSON syntax — that is what the repair attempt
    and, failing that, the degraded result are for.
    """

    text = text.strip()

    fence_match = _FENCE_RE.search(text)
    if fence_match:
        candidate = fence_match.group(1).strip()
        if candidate:
            return candidate

    # No fence: find the first '{' and the matching last '}' in the text.
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return text[start : end + 1]

    return text


def parse_action(raw_text: str) -> tuple[AgentAction | None, ActionError | None]:
    """Extract, parse, and schema-validate one `AgentAction` from raw
    model text. Returns `(action, None)` on success or `(None, error)`
    on any failure — never raises."""

    candidate = extract_json(raw_text)

    try:
        payload = json.loads(candidate)
    except json.JSONDecodeError as exc:
        return None, ActionError(kind="invalid_json", message=str(exc), raw_text=raw_text)

    try:
        action = _ACTION_ADAPTER.validate_python(payload)
    except ValidationError as exc:
        return None, ActionError(kind="invalid_schema", message=_short(str(exc)), raw_text=raw_text)

    return action, None


def build_repair_prompt(original_user_prompt: str, error: ActionError) -> str:
    """Build the single repair message sent back to the model after an
    `ActionError`. Explicit and inspectable — not a magic retry."""

    return (
        f"{original_user_prompt}\n\n"
        "--- REPAIR REQUEST ---\n"
        "Your previous response could not be used because of the following "
        f"problem: {error.kind}: {error.message}\n"
        "Respond again with EXACTLY ONE JSON object matching either the "
        "call_tool or final action shape described above. Do not include "
        "any text outside the JSON object."
    )


def degraded_result(
    *,
    request_id: str,
    error_code: str,
    error_message: str,
    tool_calls: list[ToolCallRecord],
    meta: RunMeta,
    missing_info: list[str] | None = None,
) -> TriageResult:
    """The single place a *safe degraded output* is constructed.

    `needs_human_review` is always `True` here: this function only
    exists for cases the agent could not resolve on its own. TODO: if
    you add domain-specific fields to `TriageResult` (a priority, a
    category, ...) that don't have a sensible `None`/empty default,
    decide a deliberate, documented placeholder for them here — the
    reqtriage reference build always used `category="other"`,
    `priority="P3"` rather than inventing an urgency it had no basis to
    guess. Document whatever you choose in `docs/brief.md`'s "Known
    limits", the way that build did.
    """

    return TriageResult(
        request_id=request_id,
        summary="Automated triage could not be completed for this request.",
        missing_info=missing_info or ["automated triage failed — manual review required"],
        confidence=0.0,
        needs_human_review=True,
        rationale=_short(f"{error_code}: {error_message}", limit=380),
        tool_calls=tool_calls,
        meta=meta,
        error=error_code,
    )


def _short(message: str, limit: int = 300) -> str:
    message = message.replace("\n", " ")
    return message if len(message) <= limit else message[: limit - 3] + "..."
