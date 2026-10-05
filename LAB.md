# Guided Lab — Build and Run a Real-Model Parcel Agent

## Goal

Build a small agent that can answer:

> My parcel PKG123 was due yesterday. Where is it?

The finished flow is:

```text
user request
→ real Claude model
→ model requests track_package
→ your Python validates the request
→ your Python runs track_package()
→ tool result goes back to Claude
→ Claude returns the final answer
```

The model may request the tool. **Python remains in control of execution.**

---

## Checkpoint 0 — Environment

Run:

```bash
python check_env.py
```

After dependencies and credentials are configured, the expected final line is:

```text
All checks passed. Continue with LAB.md.
```

Then verify the real model:

```bash
python model_check.py
```

Expected pattern:

```text
Connecting to runtime model...
Model responded: READY
Real-model connection works.
```

The exact capitalization of the model response is not important. A successful response proves your runtime credentials and network path work.

If either command fails, use `TROUBLESHOOTING.md` before continuing.

---

## Checkpoint 1 — Inspect what is already supplied

Open these files:

```text
prompts/system.md
prompts/user.md
data/packages.json
tools.py
llm.py
agent.py
```

Do not edit anything yet.

Be able to identify:

```text
system.md       rules given to the runtime model
user.md         current request and optional tool result
packages.json   synthetic parcel data
tools.py        normal Python function that reads parcel data
llm.py          real Claude API adapter
agent.py        orchestration code you will complete
```

Important:

> Copilot/Claude helps you WRITE the code.  
> AnthropicLLM in llm.py is what the code CALLS when it runs.

---

## Checkpoint 2 — Run the tool directly

Before involving a model, prove the ordinary Python tool works.

Run:

```bash
python tools.py PKG123
```

Expected:

```json
{
  "found": true,
  "tracking_id": "PKG123",
  "status": "Delayed",
  "location": "Penang depot",
  ...
}
```

Now try:

```bash
python tools.py DOES-NOT-EXIST
```

Expected:

```json
{
  "found": false,
  "tracking_id": "DOES-NOT-EXIST"
}
```

This proves the tool is just normal deterministic Python.

---

## Checkpoint 3 — Understand the model contract

Open `prompts/system.md`.

The model is allowed to return one of two actions.

Request the tool:

```json
{
  "action": "call_tool",
  "tool": "track_package",
  "arguments": {
    "tracking_id": "PKG123"
  }
}
```

Or finish:

```json
{
  "action": "final",
  "answer": "..."
}
```

We designed this JSON contract. It is the contract between our application and the runtime model.

The model does **not** get permission to execute arbitrary Python.

---

## Checkpoint 4 — Use Copilot/Claude to implement the agent loop

Open `agent.py`.

Most of the wiring is already present. The function you need to complete is:

```python
run_agent(request: str, llm) -> dict
```

Open `COPILOT_PROMPT.md`.

Copy the complete prompt from that file into GitHub Copilot Chat with Claude selected.

Let Claude edit `agent.py`.

Then inspect the resulting `run_agent()` before running it.

You should be able to point to:

1. where the real model is called;
2. where the model output is parsed;
3. where the tool name is checked;
4. where the one-tool budget is checked;
5. where Python executes `track_package()`;
6. where the tool result is passed back to the model;
7. where the final answer is returned.

If Claude changes unrelated files or adds more tools, undo those changes and use the bounded prompt again.

---

## Checkpoint 5 — Run the real agent

Run:

```bash
python agent.py "My parcel PKG123 was due yesterday. Where is it?"
```

Expected pattern:

```text
MODEL TURN 1
{... "action": "call_tool" ...}

TOOL
track_package('PKG123')
{... parcel evidence ...}

MODEL TURN 2
{... "action": "final" ...}

FINAL RESULT
{
  "status": "completed",
  "answer": "...",
  "model_turns": 2,
  "tool_actions": 1
}
```

The wording of the final answer can vary because this is a real model.

The important evidence is:

```text
real model called
→ approved tool requested
→ Python executed tool
→ tool result returned to model
→ final answer produced
```

---

## Checkpoint 6 — Try other requests

Run:

```bash
python agent.py "Has PKG456 already been delivered?"
```

Then:

```bash
python agent.py "Where is parcel UNKNOWN999?"
```

Observe what changes and what stays deterministic.

The model wording may vary. The local data and Python authority rules do not.

---

## Checkpoint 7 — Run deterministic tests

Now that you have experienced the real model, run:

```bash
python -m pytest -q
```

Expected after your `run_agent()` implementation is correct:

```text
4 passed
```

The tests use a tiny scripted model substitute so they can test your Python repeatedly without paying for or depending on a live model call.

---

## Checkpoint 8 — Explain the boundary

Before finishing, be able to answer:

1. What did Copilot/Claude do?
2. What did the runtime Claude model do?
3. Who actually executed `track_package()`?
4. Could the model execute a tool named `delete_package`?
5. Why were there normally two model turns but one tool action?
6. What does Python do when the model exceeds its authority?

If you can answer those from the code you ran, the lab is complete.
