# Morning Lab — Build the L2 Parcel Agent

## Morning goal

Build a small L2 agent that can answer:

> My parcel PKG123 was due yesterday. Where is it?

The finished L2 flow is:

```text
user request
→ runtime model
→ model requests track_package
→ Python validates the request
→ Python runs track_package()
→ tool result goes back to the model
→ model returns the final answer
```

L2 in this exercise means:

```text
approved tools: 1
maximum tool actions: 1
maximum model turns: 2
```

Copilot may request the tool. **Python remains in control of execution.**

Do not use `get_depot_info`, `system_l3.md`, or `fake_responses_l3.json` this morning. They are supplied for the afternoon L3 extension.

---

## Checkpoint 0 — Make the environment ready

Complete `COPILOT_SETUP.md`, then run:

```bash
python check_env.py
python model_check.py
```

Expected connection pattern:

```text
Connecting through your signed-in GitHub Copilot account...
Model responded: READY
Copilot runtime connection works.
```

If either command fails, use `TROUBLESHOOTING.md` before coding.

---

## Checkpoint 1 — Inspect only the L2 pieces

Open:

```text
prompts/system.md
prompts/user.md
data/packages.json
tools.py
llm.py
fake_responses.json
agent.py
```

For now, focus only on:

```text
track_package()
prompts/system.md
fake_responses.json
```

Identify:

```text
system.md       L2 runtime rules and JSON contract
user.md         request + current tool result
packages.json   synthetic parcel data
track_package   ordinary local Python lookup
llm.py          CopilotLLM + FakeLLM
agent.py        orchestration you will complete
```

Important:

> Copilot Chat with Claude helps you WRITE the agent.
> CopilotLLM is what your Python agent CALLS while it runs.

---

## Checkpoint 2 — Prove the L2 tool works without AI

Run:

```bash
python tools.py PKG123
```

Expected evidence includes:

```json
{
  "found": true,
  "tracking_id": "PKG123",
  "status": "Delayed",
  "location": "Penang depot"
}
```

Then:

```bash
python tools.py DOES-NOT-EXIST
```

This proves the lookup is normal deterministic Python.

---

## Checkpoint 3 — Understand the L2 contract

Open `prompts/system.md`.

The model can either request:

```json
{
  "action": "call_tool",
  "tool": "track_package",
  "arguments": {
    "tracking_id": "PKG123"
  }
}
```

or finish:

```json
{
  "action": "final",
  "answer": "..."
}
```

The JSON is an application contract. It is not permission for the model to execute Python.

---

## Checkpoint 4 — Implement only L2

Open:

```text
COPILOT_PROMPT.md
```

Copy the complete prompt into GitHub Copilot Chat with Claude selected.

Let it implement only `run_agent()` in `agent.py`.

Do not ask it to implement L3 yet.

Before running the code, identify:

1. where the model is called;
2. where JSON is parsed;
3. where `track_package` is allow-listed;
4. where the one-action budget is enforced;
5. where Python executes `track_package()`;
6. where the tool result is sent back;
7. where the final result is returned.

---

## Checkpoint 5 — Run real L2

Run:

```bash
python agent.py --mode copilot \
  "My parcel PKG123 was due yesterday. Where is it?"
```

Expected pattern:

```text
MODEL TURN 1
→ call_tool track_package

TOOL
→ parcel evidence

MODEL TURN 2
→ final

FINAL RESULT
→ completed
→ model_turns: 2
→ tool_actions: 1
```

---

## Checkpoint 6 — Run deterministic L2

Run:

```bash
python agent.py --mode fake \
  "My parcel PKG123 was due yesterday. Where is it?"
```

Run it again.

The FakeLLM model responses should be identical because `fake_responses.json` is scripted.

---

## Checkpoint 7 — Try other real L2 requests

```bash
python agent.py --mode copilot "Has PKG456 already been delivered?"
```

Then:

```bash
python agent.py --mode copilot "Where is parcel UNKNOWN999?"
```

Observe what varies and what stays deterministic.

---

## Checkpoint 8 — Prove L2 is complete

Run:

```bash
python -m pytest -q
```

Expected:

```text
4 passed
```

Do not start L3 until you have this result.

---

## Checkpoint 9 — Explain L2

Be able to answer:

1. What did Copilot Chat with Claude do?
2. What did CopilotLLM do?
3. Who executed `track_package()`?
4. How many tool actions were allowed?
5. Why were there normally two model turns but one action?
6. Could the runtime model execute `delete_package`?

## STOP HERE

When you have `4 passed`, you have a working L2 checkpoint.

Wait for the trainer to begin the afternoon section.

Then open:

```text
L3_EXTENSION.md
```
