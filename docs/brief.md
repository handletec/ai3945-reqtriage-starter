# Agent brief — capstone TEMPLATE

This is the artefact you check your own capstone build against, the
same way `docs/brief.md` was used for every checkpoint before this one.
Fill in each section as the corresponding piece of YOUR agent gets
built — don't write the whole thing up front, and don't leave a section
as prose about what you *plan* to do; write down what's actually true
of the code once it exists.

A brief is not documentation you write after the fact for someone else.
It's the thing you check new code against before you accept it: "does
this match what the brief says the agent may do?" If a coding
assistant's output does something the brief doesn't mention, that's a
signal to look closer — either the brief is out of date, or the
assistant added something you didn't ask for.

## What you're starting from

This checkpoint is a working, tested, structurally-complete agent with
NO business domain wired in yet:

- **Already done (generic infrastructure — you should not need to
  rewrite these):** a registry-based tool mechanism (`reqtriage/tools/`)
  that makes "no write authority" and "no scope creep" concrete rather
  than aspirational; a bounded agent loop with two independent budgets
  — `max_tool_actions` (the L1/L2/L3 autonomy dial) and `max_model_turns`
  (an independent safety bound) — see `reqtriage/agent.py`; a
  validation/repair layer that turns untrusted model text into a typed
  action or a safe degraded result, with exactly one repair attempt per
  run (`reqtriage/validation.py`); a deterministic policy layer that
  runs before and after the model and never calls it
  (`reqtriage/rules.py`); a `FakeLLM` you can script against with no
  network access (`reqtriage/llm/fake.py`); a CLI with a documented
  exit-code contract (`reqtriage/cli.py`); a passing test suite proving
  all of the above.
- **TODO (the domain — this is your capstone):** pick ONE narrow,
  read-only lookup/data source for a task of your choosing; add the
  fields your domain needs to `TriageProposal`/`TriageResult`
  (`reqtriage/models.py`); choose the minimum justified autonomy level;
  wire the lookup either as a model-requested `ToolSpec` (L2/L3) or as
  a deterministic program-owned lookup triggered from validated model
  domain data (L1); rewrite the prompt/models in sync; extend
  `reqtriage/rules.py::post_process` for deterministic policy and
  provenance; write the tests the mandatory scope requires (see below).

## Mandatory minimum scope

One controlled read-only lookup/data source, one positive case, and one
negative case. Concretely:

- **L1 option:** deterministic program policy invokes the read-only
  lookup after the model returns validated domain data. The model does
  not select the action, but the lookup still has a narrow contract and
  protected fields still require provenance.
- **L2/L3 option:** register one `ToolSpec` in
  `reqtriage/tools/__init__.py`, backed by read-only reference data.
- At least one sample request under `data/samples/` that should make
  the controlled lookup/data path succeed (a positive case), and at
  least one that should be refused, require human review, or degrade
  safely for a meaningful boundary (a negative case).
- At least one test proving the controlled lookup/data path works
  end-to-end and at least one proving its miss/invalid/failure boundary,
  plus one `tests/test_agent.py` end-to-end test.

More than the minimum is fine. Less isn't.

## Autonomy decision

TODO — record the chosen level (L1, L2, or L3) and why the task needs
that much autonomy and no more. If L1, state what domain data the model
returns and which deterministic policy owns the lookup. If L2/L3,
state which `call_tool` actions the model may request and the bounded
action/turn limits.

## Version identity

TODO — record the brief version, prompt version, and any model/provider
or reference-data identity that matters to reproducing or interpreting
this build.

## Objective

TODO — one or two sentences: given one free-text request in your chosen
domain, what judgement is the agent proposing, and for whom? Keep the
"it recommends, it never acts" framing from the reference build unless
you have a specific, considered reason to change it.

## Inputs

*(Mostly given — see `reqtriage/models.py::TriageRequest`.)* One
`TriageRequest` per run: `request_id`, `source`, `description` (free
text), optional `reported_by`, `submitted_at`, `tags`. TODO: does your
domain need anything `TriageRequest` doesn't already have? If so, say
what and why here before you touch the model.

## Outputs

TODO — list every field of your `TriageProposal`/`TriageResult` here,
including the 5 generic ones already there (`summary`, `missing_info`,
`confidence`, `needs_human_review`, `rationale`) plus whatever you add.
One line each: what it means and who fills it in (the model, or
`rules.post_process`).

## Allowed actions

TODO — name the controlled read-only lookup/data source, what it looks
up, and what data it touches. For L2/L3 keep this in exact sync with
`TOOL_REGISTRY`. For L1 state the deterministic policy that decides
when the lookup runs; the model must not select that action.

## Blocked actions (the agent has no authority to do any of the following)

Some of these are already true by construction and worth restating
here rather than re-deriving:

- No write tool of any kind — your capstone tool must be read-only.
- No network call anywhere except the configured LLM boundary — and at
  this checkpoint, `llm.provider = "fake"`, so not even that.
- Cannot continue indefinitely — every run is bounded by
  `max_tool_actions` and the independent `max_model_turns` safety bound
  (`config/settings.toml [agent]`).
- TODO — add anything specific to your domain: can it assign or close
  something in a real system? Notify anyone? Make the final call on
  something risky without a human seeing it?

## Success criteria

TODO — for each criterion, name the test that checks it. A success
criterion with no test behind it is a hope, not a criterion. Keep
"every run produces a schema-valid result, never a stack trace" and
"the full `pytest` suite passes with no network access" from the
reference build; add your own for whatever your tool and fields need to
prove.

## Known limits

TODO — every real system has some. What does yours deliberately not
handle well, and why is that an acceptable trade-off for the capstone
rather than an oversight? "The model's judgement quality is unverified"
belongs here unconditionally — everything in this repository runs
against `FakeLLM`, which replays scripted responses; `pytest` passing
proves the *code* handles a given model response correctly, never that
a real model's judgement would be good. See README.md, "Moving to a
real provider".

## Human-review boundaries

`needs_human_review` is already forced `True` whenever `confidence`
falls below `policy.confidence_threshold`, and whenever a run degrades
for any reason (malformed output after repair, an unresolvable action,
an exhausted turn budget, an LLM infrastructure failure). TODO: add
your own domain-specific conditions here as you add them to
`rules.post_process` — e.g. a field your tool could not confirm this
run, or a deterministic keyword floor.

## Maintenance note

TODO — name at least one likely future change, which artefact/interface
it affects, and the representative/negative/regression checks that
should be re-run. State any known operational unknowns and whether the
autonomy ceiling should be reconsidered after that change.

## Provider status

`config/settings.toml` sets `llm.provider = "fake"`. No live LLM
endpoint is configured, approved, or contacted anywhere in this
checkpoint — see `reqtriage/llm/http.py` for what completing a real
provider would require, if your course setup ever approves one.
