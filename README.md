# ReqTriage — AI3945 Capstone Starter

Course **AI3945 — Practical AI Agent Engineering in Python with VS
Code**.

**Delivery context:** hands-on examples and synthetic data are tailored to Intel Product Development Engineering staff using validation/test/failure-triage scenarios. The engineering concepts and agent architecture are unchanged; no Intel proprietary data or internal process is represented. This is the **capstone starting point** on the `capstone-starter` branch — a participant-facing workspace, not a finished agent for any specific domain. The engine
underneath (a bounded agent loop, a tool registry, validation/repair,
deterministic policy) is complete and tested; the business domain on
top of it — a tool, its fields, its prompt wording — is yours to build.

Start this branch as a **fresh workspace** when the capstone begins. Do not overwrite or copy forward the completed guided ReqTriage workspace from `main`. This branch should also not be used as a reference solution during the guided practicals.

This README is self-contained. Read `docs/brief.md` next: it is the
template you fill in as you build, and the checklist you hold your own
(or Claude's) output against before accepting it.

## What this state is

The reference build this was derived from implemented one complete,
concrete triage domain end to end — its own tool, its own result
fields, its own policy rules, all backed by a full test suite. This
checkpoint keeps every piece of *mechanism* that build proved out, and
replaces every piece of *domain content* with a small, explicit
template: a 5-field generic result shape, an empty tool registry, a
system prompt full of `[TODO: ...]` markers, and two placeholder sample
requests. Nothing here is a partially-hidden version of a more complete
answer — the domain genuinely does not exist yet in this repository.

## Audience

Participant-facing. This is the repository you build your capstone
project in. Don't go looking for a more finished copy to copy from —
picking a domain, wiring up one controlled read-only lookup/data
source, and making the tests prove it works is the exercise, not an
obstacle to it.

## Mandatory minimum scope

**One controlled read-only lookup/data source, one positive case, and
one negative case.** See `docs/brief.md` for the full breakdown.

- At **L1**, deterministic program policy may own when the lookup runs;
  the model returns domain data but does not select the action.
- At **L2/L3**, register a `ToolSpec` and let the model request only the
  bounded action vocabulary.

In both cases, protected tool-derived facts require provenance. More
autonomy is not a higher score.

Before defence, also complete the **Autonomy decision**, **Version
identity**, and **Maintenance note** sections in `docs/brief.md`; these
are part of the capstone evidence, not optional documentation.

## What's implemented (generic infrastructure — you shouldn't need to rewrite these)

- `TriageRequest`, `CallToolAction`/`FinalAction`/`AgentAction`,
  `ToolCallRecord`, `RunMeta` — full Pydantic v2 models
  (`reqtriage/models.py`).
- A provider-neutral LLM boundary (`reqtriage/llm/base.py`) with
  `FakeLLM` (`reqtriage/llm/fake.py`) as the only implemented
  provider — scripted responses replayed from
  `tests/fixtures/llm_responses/`, no network access required.
- The tool registry/allow-list mechanism (`reqtriage/tools/__init__.py`)
  — `TOOL_REGISTRY` is empty, but `dispatch_tool()` and
  `describe_result_for_model()` are complete and generic; any tool name
  the model requests right now correctly comes back `unknown_tool`.
- Honest model-usage accounting: token sums include only reported values,
  while `RunMeta.*_unreported_calls` records calls where the provider did
  not report that field, so partial totals are visibly lower bounds.
- A bounded agent loop (`reqtriage/agent.py`) with two independent
  budgets: `max_tool_actions` (the L1/L2/L3 autonomy dial) and
  `max_model_turns` (a separate safety bound that stops a misbehaving
  model even after its action budget is spent) — see that module's
  docstring for why these are two different numbers.
- A validation/repair layer (`reqtriage/validation.py`): untrusted model
  text is always turned into either a valid `AgentAction` or a safe
  degraded `TriageResult`, with exactly one repair attempt per run.
- A deterministic policy layer (`reqtriage/rules.py`) that runs before
  and after the model and never calls it — currently just a confidence
  threshold (`post_process`) and two pre-checks (`pre_check`).
- A CLI with a documented exit-code contract (`reqtriage/cli.py`),
  JSONL run logging (`reqtriage/logging_setup.py`), and an environment
  preflight (`scripts/check_env.py`).
- A passing test suite covering every piece above.

## What's intentionally absent (your job)

- **No domain and no registered tool.** `TOOL_REGISTRY` is empty;
  `TriageProposal`/`TriageResult` carry only 5 generic fields
  (`summary`, `missing_info`, `confidence`, `needs_human_review`,
  `rationale`); `prompts/triage_system.md` is a template with `[TODO]`
  markers where your tool and fields go.
- **No domain-specific policy.** `rules.post_process` only enforces the
  confidence threshold — no keyword floor, no provenance check against
  a tool's results, because there is no tool yet to check against.
- **No real sample data.** `data/samples/example_001.json` and
  `example_002.json` are placeholders (see `data/samples/README.md`) —
  replace them with requests from your own task.
- **No golden/regression test suite.** Invariant-based regression
  testing across a full sample set is something you can add once you
  have real fields worth asserting invariants about.
- No live LLM provider — `llm.provider = "fake"` only.

## Commands that work

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
python scripts/check_env.py        # preflight — run this first
python -m reqtriage data/samples/example_001.json
python -m pytest -v
```

`python scripts/check_env.py` checks Python version, exact
`pydantic`/`pytest` pins, that every required file/directory exists,
that `config/settings.toml` parses, that a sample request loads, and
that a minimal `FakeLLM` round trip completes end to end.
`python -m pytest -v` runs the full suite — the clean capstone baseline is **69 passed** with no network access required.
`python -m reqtriage data/samples/example_001.json` prints a generic
5-field `TriageResult` as JSON and appends one line to
`logs/runs.jsonl`.

## How FakeLLM works (and what it does not prove)

`llm.provider = "fake"` in `config/settings.toml` is the only provider
implemented here. `reqtriage/llm/fake.py` replays a scripted sequence of
raw text responses — one per step — from a named fixture file under
`tests/fixtures/llm_responses/`. The CLI picks a fixture per sample
request via `config/fake_llm_scenarios.json`; tests either do the same
or build a `FakeLLM` inline from a literal script for a specific case
(see `tests/test_agent.py`).

**This means everything in this repository — every test, the CLI demo —
runs with no network access and no credentials, by design.** It also
means: **passing tests prove that this codebase's parsing, validation,
tool dispatch, and policy logic handle a given model response
correctly. They prove nothing about whether a real model would produce
a *good* judgement for a real request.** Do not present a green test
suite as evidence of model quality — see "Moving to a real provider"
below for what that would actually require.

## Repository layout

```
config/settings.toml         non-secret configuration (paths, max_tool_actions/max_model_turns, policy thresholds, prompt version)
config/fake_llm_scenarios.json   maps a sample request_id -> a named FakeLLM scenario (CLI only, not used by tests)
prompts/                     the system and user prompt text, plus a changelog
docs/brief.md                 capstone brief TEMPLATE: fill in as you build your own tool and fields
docs/review_checklist.md      checklist for reviewing Claude-generated Python before accepting it
data/samples/                 two placeholder request files — replace with your own task's data
data/reference/               empty on purpose — your tool's read-only reference data goes here
logs/runs.jsonl               one JSON line per run (created on first run; gitignored)
reqtriage/                    the package — see "Where things live" below
tests/                        the pytest suite, plus tests/fixtures/llm_responses/ (FakeLLM scripts)
scripts/check_env.py          environment preflight
```

## Where things live

| If you want to change... | Edit... |
|---|---|
| Your domain's fields (what the model proposes) | `reqtriage/models.py` (`TriageProposal`/`TriageResult`) — keep `prompts/triage_system.md` in exact sync |
| What the model is told to do | `prompts/triage_system.md`, `prompts/triage_user.md` — then bump the version in both `prompts/CHANGELOG.md` and `config/settings.toml` |
| Your tool | Register a `ToolSpec` in `reqtriage/tools/__init__.py`; put its read-only data under `data/reference/` and its path in `config/settings.toml [data]` / `reqtriage/config.py`'s `DataSettings` |
| A policy rule (confidence threshold, allowed sources, or your own domain rule) | `config/settings.toml [policy]`, enforced in `reqtriage/rules.py` |
| The autonomy ceiling (L1/L2/L3) and the runaway-loop safety bound | `config/settings.toml [agent] max_tool_actions` / `max_model_turns` — see `reqtriage/agent.py`'s module docstring for why these are two separate numbers |
| The orchestration itself (the agent loop) | `reqtriage/agent.py` — read it top to bottom, it is one function |
| How malformed model output is handled | `reqtriage/validation.py` |
| What gets logged | `reqtriage/logging_setup.py` and the record built in `reqtriage/agent.py::_log_run` |

## Exit codes

| Code | Meaning |
|---|---|
| 0 | A normal `TriageResult` was produced. `needs_human_review` may be `true` or `false` — that is a business outcome, not a software failure. |
| 1 | Usage or environment problem (bad arguments, missing/invalid request file, configuration error). The agent never ran. |
| 2 | The agent ran but produced a *degraded* result (`result.error` is set) — malformed model output survived one repair attempt, an unknown/invalid action, the model-turn budget was exhausted, or the LLM call itself failed. The JSON on stdout is still a valid `TriageResult`; nothing crashed, but a human should look at it. |

## Moving to a real provider

Not done at this checkpoint — there is no approved runtime LLM/API
assumed here. If one becomes available for your capstone:

1. Complete `reqtriage/llm/http.py` (its module docstring is a
   checklist). It reads credentials via
   `reqtriage.config.get_secret()` — real environment variables only.
   Nothing in this codebase loads a `.env` file automatically; see
   `.env.example` for the variable names a human would export.
2. Set `llm.provider = "http"` in `config/settings.toml`.
3. Re-run the full `pytest` suite — it should still pass unchanged,
   because it exercises `FakeLLM`, not the provider.
4. Separately, run your own representative samples against the real
   provider and review the output by hand. This is not optional and is
   not replaced by step 3: it is the only way to learn anything about
   actual model quality, cost, and latency.
5. Update `prompts/CHANGELOG.md` and `config/settings.toml`
   `[prompts] version` together if the prompt needs adjusting for the
   new provider's behaviour.

## How to work in this repository

Read the relevant module's docstring before changing it — each one
says what's generic mechanism (leave it alone) versus a template
you're meant to replace. Give Claude a specific, bounded
task rather than an open-ended one ("register a `ToolSpec` for X that
reads from `data/reference/x.csv` and returns `None` on no match", not
"add my tool"). Review what it proposes against
`docs/review_checklist.md`, run the tests, and only then move on. Do
not go looking for a more-complete copy of this repository to build
from — this checkpoint already contains every piece of infrastructure
the capstone needs; the only thing missing is your domain.

## Known limitations

- **Model judgement quality is unverified.** Everything here runs
  against `FakeLLM`, which replays scripted responses. `pytest` passing
  proves the *code* handles a given model response correctly; it proves
  nothing about whether a real model's judgement would be good.
- **No write authority exists anywhere in this build.** Your capstone
  tool must be read-only, per the course rules — turning any
  recommendation into an actual action in a real system is out of
  scope.
- **`TOOL_REGISTRY` is empty until you register something.** Any tool
  name the model requests right now is `unknown_tool` by design, not a
  bug — see `reqtriage/tools/__init__.py`.

See `docs/brief.md`, "Known limits", for whatever you add as you build.

## Handover checklist

- [ ] `python scripts/check_env.py` passes
- [ ] `python -m pytest -v` passes
- [ ] Read `docs/brief.md` and filled in every section relevant to the
      piece of the agent you've built so far
- [ ] Read `reqtriage/agent.py` top to bottom (the whole orchestration)
- [ ] Registered at least one read-only tool in
      `reqtriage/tools/__init__.py`, with at least one positive-case and
      one negative-case test for it
- [ ] Replaced `data/samples/example_001.json` /
      `example_002.json` with real sample requests from your own task
- [ ] Know that `logs/runs.jsonl` is the first place to look when a
      result looks wrong — it records model id, prompt version, tool
      actions used, model turns used, tool calls, and outcome for every
      run
- [ ] Know that changing a prompt means bumping its version in two
      places (`prompts/CHANGELOG.md`, `config/settings.toml`)
