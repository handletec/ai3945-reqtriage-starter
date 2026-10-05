# Guided Lab — Build and Run a Copilot-Backed Parcel Agent

## Goal

Build a small L2 agent that can answer:

> My parcel PKG123 was due yesterday. Where is it?

The finished flow is:

```text
user request
→ GitHub Copilot runtime model
→ model requests track_package
→ your Python validates the request
→ your Python runs track_package()
→ tool result goes back to the runtime model
→ runtime model returns the final answer
```

Copilot may request the tool. **Python remains in control of execution.**

---

## Checkpoint 0 — Make the environment ready

First complete `COPILOT_SETUP.md`.

Then run:

```bash
python check_env.py
```

Expected final line:

```text
All local checks passed. Next run: python model_check.py
```

Now prove that your Python program can reach Copilot:

```bash
python model_check.py
```

Expected pattern:

```text
Connecting through your signed-in GitHub Copilot account...
Model responded: READY
Copilot runtime connection works.
```

If this fails, do not start coding yet. Use `TROUBLESHOOTING.md`.

---

## Checkpoint 1 — Inspect the supplied pieces

Open these files:

```text
prompts/system.md
prompts/user.md
data/packages.json
tools.py
llm.py
fake_responses.json
agent.py
```

Do not edit anything yet.

Identify each responsibility:

```text
system.md          runtime rules and JSON contract
user.md            current request + current tool result
packages.json      synthetic parcel data
tools.py           local deterministic Python lookup
llm.py             CopilotLLM + FakeLLM adapters
fake_responses     scripted FakeLLM behaviour
agent.py           orchestration you will complete
```

Important distinction:

> Copilot Chat with Claude helps you WRITE the agent.
> CopilotLLM is what the agent CALLS while it runs.

---

## Checkpoint 2 — Prove the tool works without AI

Run:

```bash
python tools.py PKG123
```

Expected evidence:

```json
{
  "found": true,
  "tracking_id": "PKG123",
  "status": "Delayed",
  "location": "Penang depot"
}
```

Now run:

```bash
python tools.py DOES-NOT-EXIST
```

Expected evidence:

```json
{
  "found": false,
  "tracking_id": "DOES-NOT-EXIST"
}
```

This proves the tool is ordinary Python. The model does not perform the lookup itself.

---

## Checkpoint 3 — Understand the model contract

Open `prompts/system.md`.

The runtime model may return only one of two action types.

Tool request:

```json
{
  "action": "call_tool",
  "tool": "track_package",
  "arguments": {
    "tracking_id": "PKG123"
  }
}
```

Final response:

```json
{
  "action": "final",
  "answer": "..."
}
```

This JSON format is **our application contract**. It is not permission for the model to execute Python.

---

## Checkpoint 4 — Use Copilot/Claude to implement only the loop

Open `agent.py`.

The missing function is:

```python
run_agent(request: str, llm) -> dict
```

Open `COPILOT_PROMPT.md`.

Copy its complete prompt into GitHub Copilot Chat with Claude selected.

Allow Claude to implement only `run_agent()`.

Before running it, inspect the result and point to:

1. where the runtime model is called;
2. where model JSON is parsed;
3. where the tool name is allow-listed;
4. where the one-tool budget is enforced;
5. where Python calls `track_package()`;
6. where the tool result is sent back to the model;
7. where the final structured result is returned.

If Claude changes other files, adds another tool, or adds a framework, undo those changes and use the bounded prompt again.

---

## Checkpoint 5 — Run the real Copilot-backed agent

Run:

```bash
python agent.py --mode copilot "My parcel PKG123 was due yesterday. Where is it?"
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

The wording can vary because this is a real model.

The evidence that matters is:

```text
real model called
→ approved tool requested
→ Python executed tool
→ tool result returned to model
→ final answer produced
```

---

## Checkpoint 6 — Run the same agent with FakeLLM

Now run:

```bash
python agent.py --mode fake "My parcel PKG123 was due yesterday. Where is it?"
```

This uses `fake_responses.json` instead of GitHub Copilot.

Run it again.

The model responses should be the same each time.

That is the purpose of FakeLLM:

```text
CopilotLLM → real model behaviour
FakeLLM    → repeatable engineering test behaviour
```

FakeLLM does not reason. It replays scripted responses.

---

## Checkpoint 7 — Try different real requests

Run:

```bash
python agent.py --mode copilot "Has PKG456 already been delivered?"
```

Then:

```bash
python agent.py --mode copilot "Where is parcel UNKNOWN999?"
```

Observe what varies and what stays deterministic.

The model wording can vary. The parcel data and Python authority rules do not.

---

## Checkpoint 8 — Run deterministic tests

Run:

```bash
python -m pytest -q
```

Expected after `run_agent()` is correct:

```text
4 passed
```

The tests use scripted model responses. They do not depend on a live Copilot request.

---

## Checkpoint 9 — Explain the boundary

Before finishing, be able to answer:

1. What did Copilot Chat with Claude do?
2. What did CopilotLLM do?
3. What did FakeLLM do?
4. Who actually executed `track_package()`?
5. Could the runtime model execute `delete_package`?
6. Why are there normally two model turns but one tool action?
7. Why is FakeLLM useful after the real-model run?

If you can answer those questions from the code you ran, the lab is complete.
