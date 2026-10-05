# Guided Lab — Build the Simple Parcel Agent

This lab is intentionally hand-held.

You do **not** need to decide the architecture. Follow each checkpoint in order. Use Claude as the development assistant, inspect its change, then run the command shown before continuing.

If a term is unfamiliar, use `CONCEPTS.md`. For common setup/runtime failures, use `TROUBLESHOOTING.md`.

Before Checkpoint 1, run `python check_env.py` and fix any FAIL result.

## What you are building

A user asks:

> My parcel PKG123 was due yesterday. Where is it?

The finished L2 flow will be:

```text
user request
→ model may request ONE approved lookup
→ Python checks the request
→ Python runs track_package()
→ result goes back to model
→ model gives final answer
```

## Files already supplied

Do not rewrite these first:

- `prompts/system.md`
- `prompts/user.md`
- `data/packages.json`
- `fake_responses.json`
- `llm.py`
- `tools.py`

Read them before starting.

---

# Checkpoint 1 — Understand the two prompts

Open:

```text
prompts/system.md
prompts/user.md
```

Be able to answer:

- Which prompt contains the rules?
- Which prompt contains the user's actual request?
- What is the only allowed tool?
- How many tool actions are permitted?

Expected answers:

```text
system.md = rules and limits
user.md   = actual request + tool result
tool      = track_package
budget    = 1 tool action
```

No coding yet.

---

# Checkpoint 2 — Ask Claude to build the smallest runner

Use this prompt:

```text
Read these files first:

- prompts/system.md
- prompts/user.md
- fake_responses.json
- llm.py
- tools.py
- agent.py

Implement only the first working FakeLLM version of agent.py.

Requirements:
- load prompts/system.md and prompts/user.md;
- use FakeLLM from llm.py;
- accept a user request from the command line;
- maximum 2 model turns;
- maximum 1 tool action;
- accept only two model actions: call_tool and final;
- the only allowed tool is track_package;
- validate the requested tool name before executing it;
- validate that tracking_id is a non-empty string;
- after a successful tool call, include its JSON result in the next user prompt;
- if the model returns final, print a structured final result;
- if a limit or authority check fails, return a clear degraded result;
- do not add another tool;
- do not add L3;
- do not add network access;
- do not change the supplied prompt, data, llm, or tool files.

Keep the implementation small and readable.
Show me the resulting agent.py before making unrelated changes.
```

Then run:

```bash
python agent.py --mode fake
```

You should see:

```text
MODEL TURN 1
→ call_tool track_package

TOOL
→ package status

MODEL TURN 2
→ final

FINAL RESULT
→ completed
→ model_turns = 2
→ tool_actions = 1
```

If you do not see this sequence, stop and compare your implementation with the requirements above.

---

# Checkpoint 3 — Explain what just happened

Before changing anything, answer these in your own words:

1. Why did FakeLLM return `track_package`?
2. Who actually executed `track_package()`?
3. Could the model call a tool named `delete_package`?
4. Why are there two model turns but only one tool action?

Expected understanding:

```text
FakeLLM returned track_package because we scripted it.
Python executed the tool.
Python only permits track_package.
Turn 1 asks for the tool; turn 2 finalises after seeing the result.
```

---

# Checkpoint 4 — Add three focused tests

Use Claude:

```text
Read the current agent.py, llm.py and tools.py.

Create tests/test_agent.py.

Add exactly these tests:

1. A normal FakeLLM run requests track_package once and then finalises.
   Assert status=completed, tool_actions=1 and model_turns=2.

2. A FakeLLM response requesting delete_package is rejected safely.
   Assert status=degraded and error=tool_not_allowed.

3. A FakeLLM script that requests a second tool after already using one
   is stopped by the tool budget.
   Assert status=degraded, error=tool_budget_exhausted and tool_actions=1.

Do not change the agent implementation unless a test exposes a real defect.
Do not add extra tools or L3 behaviour.
```

Run:

```bash
python -m pytest -q
```

Expected:

```text
3 passed
```

---

# Checkpoint 5 — Inspect the boundary

Open `agent.py`.

Find and point to:

```text
where the model response enters Python
where JSON is parsed
where the action is checked
where the tool name is allow-listed
where the tool budget is checked
where Python executes track_package()
where the tool result is given back to the model
where the final answer is returned
```

If you can identify all eight, you understand the basic L2 agent loop.

---

# Checkpoint 6 — Optional real model

Do this only after FakeLLM works.

The real adapter is already in `llm.py`; the agent should not need redesign.

Configure an OpenAI-compatible endpoint:

```bash
export LLM_URL="https://YOUR-ENDPOINT/v1/chat/completions"
export LLM_MODEL="YOUR-MODEL"
export LLM_API_KEY="YOUR-KEY"
```

Then run:

```bash
python agent.py --mode real "My parcel PKG123 was due yesterday. Where is it?"
```

Compare:

```text
FakeLLM:
known scripted behaviour
→ proves our agent machinery

Real model:
variable model judgement
→ tests whether the model follows our contract
```

## Done

You have built a small L2 agent when:

- the system and user prompts are external Markdown files;
- FakeLLM produces repeatable behaviour;
- Python alone executes tools;
- exactly one tool is allowed;
- the model gets at most one tool action;
- the result can be completed or degraded safely;
- all three tests pass.
