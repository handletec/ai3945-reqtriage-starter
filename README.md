# ReqTriage — AI3945 Guided Starter

Course **AI3945 — Practical AI Agent Engineering in Python with VS
Code**.

**Delivery context:** hands-on examples and synthetic data are tailored to Intel Product Development Engineering staff using validation/test/failure-triage scenarios. The engineering concepts and agent architecture are unchanged; no Intel proprietary data or internal process is represented. This is the **guided starting point** for the AI3945 practical sequence, not a finished agent. You will build it forward one bounded exercise at a time using **Claude as the development assistant** while keeping the Python runtime-model boundary separate.

## Branch role

This `main` branch is the guided ReqTriage workspace used through the Day 1 and Day 2 morning practicals. Keep building forward in this branch. When the capstone begins, start a **fresh workspace** from the separate `capstone-starter` branch rather than copying the completed guided build into the capstone.

Do not use `capstone-starter` as an answer source for the guided practicals; it contains generic infrastructure intentionally reserved for the independent capstone.

## How to work in this repository

For each exercise: read the relevant module's docstring (it tells you
what's a stub, what's complete, and what to build), give Claude a specific, bounded engineering task rather than an open-ended
one, review what it proposes against `docs/review_checklist.md`, run the
tests, and only then move on. Do not go looking for a more complete
version of this repository to copy from — working through the failures
and corrections yourself is the point of the exercise, not an obstacle
to it.

## What's implemented (complete scaffolding — you shouldn't need to change these)

- `TriageRequest` (`reqtriage/models.py`) — the input schema.
- The LLM boundary interface: `LLMResponse` and `LLMClient`
  (`reqtriage/llm/base.py`).
- Configuration (`reqtriage/config.py`) — paths to the sample requests
  and reference data.
- Console logging (`reqtriage/logging_setup.py`).
- CLI argument parsing and request-file loading/validation
  (`reqtriage/cli.py`) — up to the point where it would call a model.
- Synthetic request data (`data/samples/*.json`, 15 requests) and
  component-owner reference data (`data/reference/component_owners.csv`)
  you'll need for later exercises.
- An environment preflight (`scripts/check_env.py`).
- A passing test suite for everything above (`tests/`).

## What's a stub — this is your first exercise

- **`reqtriage/llm/fake.py`** — `FakeLLM` is not implemented. Read its
  module docstring for a bounded engineering task you can hand to a
  development assistant, what to check in the result, and how to validate it.
- **`tests/test_fake_llm.py`** — a test scaffold for `FakeLLM`, marked
  `xfail` until you implement it. Filling in the TODOs here alongside
  your implementation (not after) is part of the exercise.
- **`reqtriage/models.py`** — `TriageProposal`, `AgentAction`,
  `ToolCallRecord`, `RunMeta`, and `TriageResult` are documented stubs.
  Each belongs to a later exercise — don't fill them in ahead of time;
  each module's docstring tells you what precedes it.
- **`docs/brief.md`** — a template with most sections marked TODO. Fill
  each section in as the corresponding piece of the agent gets built,
  not all at once now.

## What's intentionally absent

- No structured `TriageResult`, no tool of any kind, no bounded agent
  loop, no policy/validation layer. Nothing here is a partially-hidden
  version of a later checkpoint — it doesn't exist yet in this
  repository at all.
- This repository and its deterministic core exercises run through a
  fake, scripted LLM provider: no live LLM provider, no credentials, and
  no network access are required to complete these exercises or to run
  the test suite, and classroom continuity never depends on a live call
  succeeding. This is a property of the repository's exercises, not a
  statement about the course as a whole: the approved course outline
  separately lists access to an approved LLM service/API as a course
  prerequisite, and once an approved runtime endpoint is available, the
  appropriate live-runtime exercises/demos use the same provider-boundary concept. A live runtime provider is intentionally not implemented in this guided starter.

## Commands that work right now

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
python scripts/check_env.py        # preflight — run this first
python -m reqtriage data/samples/req_001.json
python -m pytest -v
```

`python -m reqtriage data/samples/req_001.json` currently loads and
validates the request file and prints it back as JSON — it doesn't call
a model yet. `python -m pytest -v` should report **10 passed, 4 xfailed**. The xfails are deliberate `FakeLLM` exercise scaffolds, not a broken suite.

## Repository layout

```
data/samples/                     15 synthetic request files, data/samples/req_NNN.json
data/reference/component_owners.csv   read-only lookup data for a tool you'll build later
docs/brief.md                     agent brief TEMPLATE — fill in as you build
docs/review_checklist.md          checklist for reviewing Claude-generated Python before accepting it
reqtriage/                        the package — see module docstrings for what's complete vs. a stub
tests/                            the test suite, including scaffolds for not-yet-implemented pieces
scripts/check_env.py              environment preflight
```

## Where things live

| If you want to... | Look at... |
|---|---|
| Understand the input schema | `reqtriage/models.py::TriageRequest` |
| Understand the LLM boundary you'll implement against | `reqtriage/llm/base.py` |
| Do your first exercise | `reqtriage/llm/fake.py` and `tests/test_fake_llm.py` |
| See what configuration is already wired up | `reqtriage/config.py` |
| See the CLI's current behaviour and its next TODO | `reqtriage/cli.py` |

## Exit codes (current — will grow as the CLI grows)

| Code | Meaning |
|---|---|
| 0 | The request file loaded and validated successfully. |
| 1 | Usage or environment problem (bad arguments, missing/invalid request file, or a schema violation). |
