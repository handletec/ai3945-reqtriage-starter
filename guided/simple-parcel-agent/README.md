# AI3945 Guided Lab — Simple Parcel Agent

## Start here

This is a small, deliberately simple **L2 agent**. It exists to make the agent mechanics obvious before you work with a larger example.

You are assumed to be comfortable with normal software development. You are **not** expected to already understand agent terminology, model boundaries, tool calling, FakeLLM, or autonomy levels.

Read this file first, then follow `LAB.md` in order.

## The problem

A user asks:

> My parcel PKG123 was due yesterday. Where is it?

The agent is allowed to do one thing before answering: ask Python to run the read-only `track_package` tool.

The finished flow is:

```text
user request
→ model decides whether it needs the approved lookup
→ Python validates the request
→ Python runs track_package()
→ tool result goes back to the model
→ model gives the final answer
```

The model never executes Python itself.

## The three roles in this lab

### 1. Claude — development-time coding assistant

You use Claude to help write or change the Python files during the lab.

Claude is **not** the runtime model inside the parcel agent.

### 2. FakeLLM — predictable runtime model substitute

During development, the agent uses `FakeLLM` instead of a real model.

FakeLLM does not reason. It returns responses that we already scripted in `fake_responses.json`.

This removes model variability while we prove that our Python control flow works.

### 3. Python — the authority and execution layer

Python decides whether a requested tool is allowed, validates its arguments, enforces the tool budget, executes the tool, and stops the run when limits are reached.

The model may **request** an action. Python decides whether that request may actually execute.

## Why this is L2

For this course:

```text
L1 = model classifies; Python chooses the action
L2 = model may choose ONE approved action
L3 = model may choose a bounded sequence of approved actions
```

This lab is L2 because the runtime model can explicitly request `track_package`, but only once.

## System prompt and user prompt

The runtime model receives two prompts.

`prompts/system.md` contains the rules:

- what the model is supposed to do;
- the tool it may request;
- the JSON response shapes;
- the one-tool limit;
- what it must not invent.

`prompts/user.md` contains the actual request being processed and, after a tool call, the tool result.

A useful shorthand is:

```text
system prompt = rules and boundaries
user prompt   = the thing to work on
```

## Who defines the JSON format?

We do.

The application defines the model-output contract. In this lab the model must return either:

```json
{
  "action": "call_tool",
  "tool": "track_package",
  "arguments": {
    "tracking_id": "PKG123"
  }
}
```

or:

```json
{
  "action": "final",
  "answer": "Your parcel is delayed."
}
```

This is **our agent contract**. It is not the JSON envelope used internally by Claude, OpenAI, Qwen, or another provider API.

## Why use FakeLLM?

Suppose the agent breaks while using a real model. Two things may have changed:

1. our Python code;
2. the model's response.

FakeLLM removes the second variable.

If the same scripted response goes in every time, we can test the Python reliably.

Use this mental model:

> FakeLLM tests the agent engineering. A real model tests the model's judgement.

## Folder map

```text
.
├── README.md                 ← start here
├── LAB.md                    ← follow this step by step
├── CONCEPTS.md               ← agent concepts used in this lab
├── TROUBLESHOOTING.md        ← common problems and first fixes
├── requirements.txt          ← lab dependency
├── check_env.py              ← verify the local lab setup
├── agent.py                  ← intentionally incomplete at the start
├── llm.py                    ← FakeLLM + optional real-model adapter
├── tools.py                  ← approved read-only tool
├── fake_responses.json       ← scripted FakeLLM responses
├── data/
│   └── packages.json         ← synthetic parcel data
└── prompts/
    ├── system.md             ← runtime rules
    └── user.md               ← runtime request template
```

## Setup

Run these commands from **this directory**.

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python check_env.py
```

### Windows PowerShell

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python check_env.py
```

Expected final line:

```text
All checks passed. Open LAB.md and start at Checkpoint 1.
```

## Working rule

For every checkpoint:

1. read the checkpoint before prompting Claude;
2. give Claude only the bounded task shown;
3. inspect the change;
4. run the command yourself;
5. compare the real output with the expected output;
6. do not continue until the checkpoint works.

Do not ask Claude to "finish the whole agent". The point is to understand each boundary as it is added.

## Continue

Open `LAB.md` and begin at **Checkpoint 1**.
