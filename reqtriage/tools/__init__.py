"""The tool registry — the agent's entire allow-list.

CAPSTONE TEMPLATE. This mechanism is generic and complete —
`TOOL_REGISTRY`, `ToolSpec`, `dispatch_tool()`, and
`describe_result_for_model()` should not need to change shape. What's
missing is a tool: `TOOL_REGISTRY` is empty below, so right now the
model can name any tool it likes and every single one comes back
`"unknown_tool"`. Adding your own capstone tool means adding one
`ToolSpec` entry here and one branch to `describe_result_for_model()` —
see the TODOs below — not changing how dispatch works.

If a tool is not a key in `TOOL_REGISTRY`, the model cannot make the
program do it, full stop. This is the concrete mechanism behind "no
write authority" and "no scope creep": adding a capability to the agent
means adding a narrow, typed, reviewed entry here, not the model
inventing an action name at runtime. Your capstone tool must be
READ-ONLY — no write tools, per the course rules.

`dispatch_tool()` is the only way `agent.py` ever calls a tool. It never
lets an exception escape for an *expected* failure kind — unknown tool
name, arguments that fail the tool's own argument schema, or the tool's
own declared `ToolError` for an infrastructure problem (a missing or
corrupt reference-data file) all become a `ToolCallRecord` with a
`status`, not a traceback. Only a genuine bug (a tool raising something
it never declared) is allowed to propagate, and `agent.py` treats that as
a fatal run failure and degrades safely.

This module draws a hard line between two things that must never be
confused (see each function's docstring for the full reasoning):

* `dispatch_tool()` returns a `ToolCallRecord` — a concise AUDIT row for
  `TriageResult.tool_calls` and `logs/runs.jsonl`.
* `describe_result_for_model()` returns the narrow RUNTIME TOOL RESULT —
  the actual data fed back to the model so it can reason from it.

`agent.py` calls both, for different purposes, on the same tool call.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Callable

from pydantic import BaseModel, ValidationError

from reqtriage.config import Settings
from reqtriage.models import ToolCallRecord

# TODO: import your tool's function, its Pydantic args model, and any
# result/record types it needs — the way the reqtriage reference build
# did with `from reqtriage.tools.owners import LookupOwnerArgs,
# OwnerRecord, ToolError, lookup_owner`.


@dataclass(frozen=True)
class ToolSpec:
    func: Callable[..., Any]
    args_model: type[BaseModel]
    description: str


# TODO: add a small wrapper like this for your tool, matching the
# `(args, settings) -> result` shape `TOOL_REGISTRY` expects:
#
# def _run_my_tool(args: MyToolArgs, settings: Settings) -> MyToolResult | None:
#     return my_tool(args.some_field, reference_path=settings.data.my_reference_path)


TOOL_REGISTRY: dict[str, ToolSpec] = {
    # TODO: register your tool here, e.g.:
    # "my_tool": ToolSpec(
    #     func=_run_my_tool,
    #     args_model=MyToolArgs,
    #     description="One sentence describing what it looks up and what it returns on no match.",
    # ),
}


def dispatch_tool(
    tool_name: str, arguments: dict[str, Any], settings: Settings, step: int
) -> tuple[Any, ToolCallRecord]:
    """Validate and run one tool call. Always returns a `ToolCallRecord`;
    never raises for an expected failure kind (see module docstring).

    Returns `(raw_result, record)`. `raw_result` is `None` whenever
    `record.status != "ok"` — callers must check `record.status`, not
    truthiness of `raw_result`, because a legitimate "not found" also
    yields `None`/empty and is distinct from an error.
    """

    started = time.monotonic()
    spec = TOOL_REGISTRY.get(tool_name)

    if spec is None:
        record = ToolCallRecord(
            step=step,
            tool_name=tool_name,
            arguments=arguments,
            status="unknown_tool",
            error=f"'{tool_name}' is not in the tool allow-list",
            duration_ms=_elapsed_ms(started),
        )
        return None, record

    try:
        parsed_args = spec.args_model.model_validate(arguments)
    except ValidationError as exc:
        record = ToolCallRecord(
            step=step,
            tool_name=tool_name,
            arguments=arguments,
            status="invalid_arguments",
            error=_short(str(exc)),
            duration_ms=_elapsed_ms(started),
        )
        return None, record

    try:
        result = spec.func(parsed_args, settings)
    except Exception as exc:  # noqa: BLE001 — your tool should declare a
        # narrower ToolError; this is a template-level fallback so a
        # missing declaration degrades safely instead of crashing the
        # run. Narrow this to your tool's own error type once it exists,
        # the way the reqtriage reference build caught `ToolError`
        # specifically.
        record = ToolCallRecord(
            step=step,
            tool_name=tool_name,
            arguments=arguments,
            status="error",
            error=_short(str(exc)),
            duration_ms=_elapsed_ms(started),
        )
        return None, record

    status = "ok"
    if result is None or (isinstance(result, list) and len(result) == 0):
        status = "not_found"

    record = ToolCallRecord(
        step=step,
        tool_name=tool_name,
        arguments=arguments,
        status=status,
        result_summary=_summarise(result),
        duration_ms=_elapsed_ms(started),
    )
    return result, record


def describe_result_for_model(tool_name: str, raw_result: Any, status: str) -> dict[str, Any]:
    """Build the RUNTIME TOOL RESULT — the narrow, structured data that
    is actually fed back to the model as data for its next turn.

    This is deliberately a different function, with a different return
    shape, from `ToolCallRecord` (the audit/log record `dispatch_tool`
    returns above). `ToolCallRecord.result_summary` is a short string
    for a human reading logs; what this function returns is the real
    fields the tool's contract allows the model to reason from. Getting
    these two mixed up was a real bug in an earlier version of the
    reference build — the model was only ever shown `result_summary`
    and had no way to have legitimately known the details it then
    stated. `agent.py` calls this, never the record, to build the
    `tool_results` it puts in the prompt.

    TODO: add a branch here for your tool, following the pattern the
    comment shows — exactly the fields a human would want handed to
    them, and nothing from the rest of the backing dataset.
    """

    # if tool_name == "my_tool":
    #     if isinstance(raw_result, MyToolResult):
    #         return {
    #             "tool_name": tool_name,
    #             "status": status,
    #             "field_one": raw_result.field_one,
    #             "field_two": raw_result.field_two,
    #         }
    #     return {"tool_name": tool_name, "status": status}

    # An unknown tool, invalid arguments, or an infrastructure error has
    # no narrow result to hand over — only the status is meaningful.
    return {"tool_name": tool_name, "status": status}


def _elapsed_ms(started: float) -> float:
    return (time.monotonic() - started) * 1000.0


def _short(message: str, limit: int = 300) -> str:
    message = message.replace("\n", " ")
    return message if len(message) <= limit else message[: limit - 3] + "..."


def _summarise(result: Any) -> str:
    if result is None:
        return "no match"
    if isinstance(result, list):
        if not result:
            return "no matches"
        return f"{len(result)} match(es)"
    return str(result)
