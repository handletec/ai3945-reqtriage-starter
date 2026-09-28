"""The agent: `run_triage()`.

Read this function top-to-bottom; nothing about it is hidden behind a
framework. It is the exact mechanism the course architecture calls out
for the autonomy dial — and the autonomy dial is TWO separate numbers,
not one:

  * `tool_actions_used` / `max_tool_actions` — how many `call_tool`
    action opportunities the model has spent so far / may spend in
    total this run. Once a request passes the budget check and enters
    dispatch it spends one opportunity, even if the tool name is
    unknown, its arguments are invalid, or the tool itself fails.
    This is the literal L1/L2/L3 knob:
    L1 = 0, L2 = 1, L3 = a small number greater than 1.
  * `model_turns_used` / `max_model_turns` — how many times the model
    has been called at all so far / is allowed to be called in total.
    This is a SEPARATE, independent safety bound. It exists because
    "the model may only take one tool action" (L2) and "the model may
    only speak once" are different rules: an L2 run legitimately needs
    at least two turns (one to ask for the tool, one to finalise with
    the result in hand), and a misbehaving model can burn through turns
    without spending another tool action after the action budget is
    already exhausted. An unknown/invalid request that reaches dispatch
    while budget remains DOES spend an action opportunity.

An earlier version of this file used a single `max_steps` for both
ideas. That was wrong: with `max_steps=1`, a model that legitimately
asked for one tool would never get the follow-up turn needed to
finalise, and the run would incorrectly degrade as "max steps
exceeded" even though it did exactly what L2 asks for. Do not
reintroduce a single combined counter.

What exactly prevents this agent from running forever? Two independent,
explicit checks inside the loop below:

1. `if model_turns_used >= max_model_turns: give up` — checked at the
   top of every turn, before the model is even called again.
2. `if tool_actions_used >= max_tool_actions: refuse the tool call` —
   checked whenever the model asks for a tool; the tool is never
   executed once the budget is spent, no matter how many more times the
   model asks.

A SECOND correction, made after the above was already reviewed: every
real `llm.complete()` invocation must go through the SAME accounting —
normal loop turns AND the one validation-repair call. An earlier version
of this file called `llm.complete()` directly in two places (the main
loop and the repair branch) and only the main-loop call incremented
`model_turns_used` or was reflected in `RunMeta`'s token totals. That
under-counted real model usage and meant a run could make more actual
model calls than `max_model_turns` claimed to allow — exactly the kind
of silent budget leak `max_model_turns` exists to prevent. The fix is
`call_model()` below: it is now the ONLY function in this file allowed
to call `llm.complete()`, and both call sites (the main loop and the
repair branch) go through it, so a turn is spent and usage is recorded
identically either way — and if no turn budget remains, the repair call
is never attempted at all; the run degrades safely instead.

High-level shape:

    pre_check                                   (rules.py — no model call)
      -> bounded turn loop, each turn:
           call_model(...)                              (below — checks
                                                           the turn budget,
                                                           spends one turn,
                                                           accumulates
                                                           token usage;
                                                           returns None if
                                                           no budget is
                                                           left)
           parse + validate its action                   (validation.py;
                                                            one repair
                                                            attempt total
                                                            per run, ALSO
                                                            through
                                                            call_model)
           if "final": stop
           if "call_tool":
             if tool_actions_used == max_tool_actions:
               refuse — tell the model its budget is spent, loop again
             else:
               dispatch it (tools/*.py), feed the NARROW result back as
               data (tools.describe_result_for_model — never the audit
               record), loop again
      -> if the loop produced a usable proposal:
           post_process                          (rules.py — no model call)
           assemble TriageResult
         else:
           degraded_result                       (validation.py)
      -> log + return
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import datetime, timezone

from reqtriage import prompts, rules, validation
from reqtriage.config import Settings
from reqtriage.llm.base import LLMClient, LLMResponse
from reqtriage.logging_setup import append_run_log, get_logger
from reqtriage.models import CallToolAction, FinalAction, RunMeta, ToolCallRecord, TriageRequest, TriageResult
from reqtriage.tools import describe_result_for_model, dispatch_tool


@dataclass
class _ModelUsage:
    """Run-scoped accounting for real model invocations.

    `turns_used` counts every `llm.complete()` call this run makes.

    Token totals are honest aggregates:
    - a reported value contributes to the numeric sum;
    - an unreported value increments the matching unreported-call count;
    - if no call reports a field, its numeric total remains `None`;
    - if some calls report and some do not, the numeric sum is explicitly
      partial / a lower bound because the unreported-call count is > 0.
    """

    turns_used: int = 0
    prompt_tokens_total: int | None = None
    completion_tokens_total: int | None = None
    prompt_tokens_unreported_calls: int = 0
    completion_tokens_unreported_calls: int = 0

    def record_usage(self, response: LLMResponse) -> None:
        """Accumulate one completed response without inventing usage."""

        if response.prompt_tokens is None:
            self.prompt_tokens_unreported_calls += 1
        else:
            self.prompt_tokens_total = (self.prompt_tokens_total or 0) + response.prompt_tokens

        if response.completion_tokens is None:
            self.completion_tokens_unreported_calls += 1
        else:
            self.completion_tokens_total = (self.completion_tokens_total or 0) + response.completion_tokens

    def record_unreported_response(self) -> None:
        """Record a real model call that returned no usage-bearing response."""

        self.prompt_tokens_unreported_calls += 1
        self.completion_tokens_unreported_calls += 1


def run_triage(request: TriageRequest, llm: LLMClient, settings: Settings) -> TriageResult:
    logger = get_logger()
    started_monotonic = time.monotonic()
    started_at_iso = datetime.now(timezone.utc).isoformat()

    max_tool_actions = settings.agent.max_tool_actions
    max_model_turns = settings.agent.max_model_turns

    # --- Pre-checks: deterministic, no model call. ---
    pre_failure = rules.pre_check(request, settings)
    if pre_failure is not None:
        result = validation.degraded_result(
            request_id=request.request_id,
            error_code=pre_failure.code,
            error_message=pre_failure.message,
            tool_calls=[],
            meta=RunMeta(
                model_id=settings.llm.model_id,
                prompt_version=settings.prompts.version,
                started_at=started_at_iso,
                duration_ms=_elapsed_ms(started_monotonic),
                tool_actions_used=0,
                model_turns_used=0,
                repair_used=False,
            ),
            missing_info=pre_failure.missing_info,
        )
        logger.info("request %s rejected before model call: %s", request.request_id, pre_failure.code)
        _log_run(result, settings)
        return result

    system_prompt = prompts.load_system_prompt(settings)

    usage = _ModelUsage()

    def call_model(user_prompt: str) -> LLMResponse | None:
        """The ONLY place `llm.complete()` is ever invoked during this
        run. Both call sites below — the main loop and the one
        validation-repair attempt — go through here, so a model turn is
        spent and usage is accumulated identically either way.

        Returns `None`, WITHOUT calling the model at all, if the
        `max_model_turns` budget is already spent — the caller must
        treat that exactly like "no turns left" (i.e. degrade safely)
        rather than call the model "just this once anyway". This is
        what makes the repair attempt obey the same hard bound as every
        other call: a run that has already used its last turn on a
        malformed response does not get a bonus turn to repair it.

        Raises whatever `llm.complete()` raises for a genuine
        infrastructure failure — this function does not swallow that;
        the caller decides what a failed call means for the run.
        """

        if usage.turns_used >= max_model_turns:
            return None
        usage.turns_used += 1
        try:
            response = llm.complete(system=system_prompt, user=user_prompt)
        except Exception:
            usage.record_unreported_response()
            raise
        usage.record_usage(response)
        return response

    tool_calls: list[ToolCallRecord] = []
    tool_results_for_rules: list[tuple[ToolCallRecord, object]] = []
    tool_results_for_model: list[dict] = []
    repair_used = False
    tool_actions_used = 0
    error_code: str | None = None
    error_message: str = ""
    proposal = None
    last_response: LLMResponse | None = None

    user_prompt = prompts.render_user_prompt(settings, request.model_dump(), tool_results=[])

    while True:
        try:
            response = call_model(user_prompt)
        except Exception as exc:  # a real provider's infra failure — never let this crash the run
            error_code, error_message = "llm_call_failed", str(exc)
            break

        if response is None:
            # The safety bound, not the action budget, is what stopped
            # this run: the model kept talking without ever finalising,
            # whether or not it was still spending real tool actions.
            error_code = "max_model_turns_exceeded"
            error_message = f"model did not return a final action within {max_model_turns} turn(s)"
            break

        last_response = response
        current_action, act_error = validation.parse_action(last_response.text)

        if act_error is not None and not repair_used:
            logger.warning(
                "request %s: turn %d produced an unusable response (%s) — attempting one repair",
                request.request_id, usage.turns_used, act_error.kind,
            )
            repair_prompt = validation.build_repair_prompt(user_prompt, act_error)
            try:
                repaired_response = call_model(repair_prompt)
            except Exception as exc:
                # A real repair call WAS made — it just failed at the
                # infrastructure level, same as any other call_model
                # failure. It still spent a turn (call_model increments
                # the turn counter before invoking llm.complete()).
                repair_used = True
                error_code, error_message = "llm_call_failed", str(exc)
                break
            if repaired_response is None:
                # Defect fix: the repair call is NOT exempt from
                # max_model_turns. If the budget is already spent, we do
                # not attempt "one more call anyway" — no repair call is
                # made at all (repair_used stays False, since nothing
                # was actually attempted), and we degrade safely with
                # the original malformed response as the reason.
                logger.warning(
                    "request %s: no model-turn budget left to attempt the repair call",
                    request.request_id,
                )
                error_code = "max_model_turns_exceeded"
                error_message = f"model did not return a final action within {max_model_turns} turn(s)"
                break
            repair_used = True
            last_response = repaired_response
            current_action, act_error = validation.parse_action(last_response.text)

        if act_error is not None:
            error_code = f"invalid_action_{act_error.kind}"
            error_message = act_error.message
            break

        if isinstance(current_action, FinalAction):
            proposal = current_action.result
            break

        # Only one shape is left: the model is asking to call a tool.
        assert isinstance(current_action, CallToolAction)

        if tool_actions_used >= max_tool_actions:
            # The tool-action budget is spent. The tool is NOT executed —
            # not for a known tool, not for an unknown one, not for
            # anything — this is the concrete enforcement of the L2/L3
            # ceiling. Record the refusal for the audit trail and tell
            # the model plainly, then loop back around (still bounded by
            # max_model_turns above).
            logger.warning(
                "request %s: turn %d requested tool '%s' but the %d-action budget is already spent",
                request.request_id, usage.turns_used, current_action.tool_name, max_tool_actions,
            )
            refusal_record = ToolCallRecord(
                step=usage.turns_used,
                tool_name=current_action.tool_name,
                arguments=current_action.arguments,
                status="action_limit_reached",
                error=f"tool-action budget ({max_tool_actions}) already spent this run",
                duration_ms=0.0,
            )
            tool_calls.append(refusal_record)
            tool_results_for_model.append(
                {
                    "tool_name": current_action.tool_name,
                    "status": "action_limit_reached",
                    "note": (
                        f"You have already used all {max_tool_actions} tool action(s) allowed "
                        "for this run. No further tool calls will be executed. Respond now with "
                        "a final action using whatever information you already have."
                    ),
                }
            )
            user_prompt = prompts.render_user_prompt(
                settings, request.model_dump(), tool_results=tool_results_for_model
            )
            continue

        tool_actions_used += 1
        raw_result, record = dispatch_tool(
            current_action.tool_name, current_action.arguments, settings, step=usage.turns_used
        )
        tool_calls.append(record)
        tool_results_for_rules.append((record, raw_result))
        if record.status == "error":
            logger.warning(
                "request %s: tool %s failed at turn %d: %s",
                request.request_id, current_action.tool_name, usage.turns_used, record.error,
            )

        # The model gets the NARROW runtime tool result, never the audit
        # record — see tools.describe_result_for_model's docstring.
        tool_results_for_model.append(
            describe_result_for_model(current_action.tool_name, raw_result, record.status)
        )
        user_prompt = prompts.render_user_prompt(
            settings, request.model_dump(), tool_results=tool_results_for_model
        )

    duration_ms = _elapsed_ms(started_monotonic)
    meta = RunMeta(
        model_id=last_response.model_id if last_response else settings.llm.model_id,
        prompt_version=settings.prompts.version,
        started_at=started_at_iso,
        duration_ms=duration_ms,
        tool_actions_used=tool_actions_used,
        model_turns_used=usage.turns_used,
        repair_used=repair_used,
        prompt_tokens=usage.prompt_tokens_total,
        completion_tokens=usage.completion_tokens_total,
        prompt_tokens_unreported_calls=usage.prompt_tokens_unreported_calls,
        completion_tokens_unreported_calls=usage.completion_tokens_unreported_calls,
    )

    if proposal is None:
        result = validation.degraded_result(
            request_id=request.request_id,
            error_code=error_code or "unknown_failure",
            error_message=error_message,
            tool_calls=tool_calls,
            meta=meta,
        )
        logger.info("request %s degraded: %s", request.request_id, result.error)
    else:
        adjusted = rules.post_process(request, proposal, tool_results_for_rules, settings)
        result = TriageResult(
            request_id=request.request_id,
            tool_calls=tool_calls,
            meta=meta,
            error=None,
            **adjusted.model_dump(),
        )
        logger.info(
            "request %s: needs_human_review=%s confidence=%.2f",
            request.request_id, result.needs_human_review, result.confidence,
        )

    _log_run(result, settings)
    return result


def _elapsed_ms(started_monotonic: float) -> float:
    return (time.monotonic() - started_monotonic) * 1000.0


def _log_run(result: TriageResult, settings: Settings) -> None:
    record = {
        "request_id": result.request_id,
        "outcome": "degraded" if result.error else "completed",
        "error": result.error,
        "needs_human_review": result.needs_human_review,
        "confidence": result.confidence,
        "tool_call_count": len(result.tool_calls),
        "tool_calls": [
            {"tool_name": tc.tool_name, "status": tc.status, "duration_ms": tc.duration_ms}
            for tc in result.tool_calls
        ],
        "tool_actions_used": result.meta.tool_actions_used,
        "model_turns_used": result.meta.model_turns_used,
        "repair_used": result.meta.repair_used,
        "model_id": result.meta.model_id,
        "prompt_version": result.meta.prompt_version,
        "duration_ms": result.meta.duration_ms,
        "prompt_tokens": result.meta.prompt_tokens,
        "completion_tokens": result.meta.completion_tokens,
        "prompt_tokens_unreported_calls": result.meta.prompt_tokens_unreported_calls,
        "completion_tokens_unreported_calls": result.meta.completion_tokens_unreported_calls,
        "started_at": result.meta.started_at,
    }
    append_run_log(record, settings.logging.log_path)
