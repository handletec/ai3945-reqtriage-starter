# AI3945 — Trainer Complete Parcel Agent

This branch is the completed trainer version of the simplified parcel-agent lab.

It demonstrates **L2 and L3 using the same agent architecture**.

The only thing that changes between L2 and L3 is the bounded authority granted by Python.

## Branch

```text
trainer-complete-claude
```

## Runtime choices

Real Claude:

```bash
python agent.py --mode claude --level l2
python agent.py --mode claude --level l3
```

Deterministic FakeLLM:

```bash
python agent.py --mode fake --level l2
python agent.py --mode fake --level l3
```

## The L2/L3 comparison

Both levels use the same default question:

```text
My parcel PKG123 is delayed. Can I collect it from the depot today?
```

L2 authority:

```text
Allowed tools: track_package
Tool-action budget: 1
Model-turn budget: 2
```

L2 can establish that the parcel is delayed at the Penang depot, but it cannot independently verify depot collection information.

L3 authority:

```text
Allowed tools: track_package, get_depot_info
Tool-action budget: 2
Model-turn budget: 3
```

L3 can perform the parcel lookup, use the returned depot name for a second lookup, and then produce the final answer.

That is the teaching point:

> L3 is not a different or magically smarter model. The same agent has been granted more bounded authority to continue acting.

## Install

```bash
python -m pip install -r requirements.txt
```

Follow `CLAUDE_SETUP.md` to configure the real Claude runtime.

## Preflight

```bash
python check_env.py
python list_models.py
python model_check.py
python -m pytest -q
```

Expected:

```text
8 passed
```

## Recommended classroom sequence

First show deterministic L2:

```bash
python agent.py --mode fake --level l2
```

Then deterministic L3:

```bash
python agent.py --mode fake --level l3
```

Then repeat with Claude:

```bash
python agent.py --mode claude --level l2
python agent.py --mode claude --level l3
```

The program prints the current authority before every run.

## Model and effort controls

Defaults:

```text
model  = claude-sonnet-5-5
effort = medium
```

Override them:

```bash
python agent.py \
  --mode claude \
  --level l3 \
  --model claude-sonnet-5-5 \
  --effort high
```

Or use:

```text
ANTHROPIC_MODEL
ANTHROPIC_EFFORT
ANTHROPIC_MAX_TOKENS
```

## Files worth showing participants

```text
agent.py
tools.py
prompts/system.md
prompts/user.md
data/packages.json
data/depots.json
fake_responses_l2.json
fake_responses_l3.json
```

The core boundary remains:

> The model requests an action. Python decides whether the action is within the current authority and executes it.
