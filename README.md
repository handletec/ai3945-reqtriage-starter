# AI3945 — Trainer Complete Parcel Agent

This branch is the **completed trainer version** of the simplified parcel-agent lab.

It uses:

- Claude through the Anthropic API for the real runtime;
- FakeLLM for deterministic demonstration/testing;
- the same external `prompts/system.md` and `prompts/user.md` used by the participant exercise;
- the same local `track_package()` tool and synthetic parcel data.

The agent loop is already implemented. You do not need Copilot.

## Branch

```text
trainer-complete-claude
```

Clone directly:

```bash
git clone --branch trainer-complete-claude --single-branch https://github.com/handletec/ai3945-reqtriage-starter.git
cd ai3945-reqtriage-starter
```

## Install

```bash
python -m pip install -r requirements.txt
```

Then follow `CLAUDE_SETUP.md` to set `ANTHROPIC_API_KEY`.

## Preflight

```bash
python check_env.py
python model_check.py
python -m pytest -q
```

Expected tests:

```text
4 passed
```

## Run the deterministic demo

```bash
python agent.py --mode fake
```

Expected flow:

```text
MODEL TURN 1
→ call_tool track_package(PKG123)

TOOL
→ local parcel evidence

MODEL TURN 2
→ final answer

FINAL RESULT
→ completed, 2 model turns, 1 tool action
```

## Run the real Claude demo

```bash
python agent.py --mode claude
```

Or:

```bash
python agent.py --mode claude "Has PKG456 already been delivered?"
```

## Model and effort controls

The code supports both.

Default:

```text
model  = claude-sonnet-5-5
effort = medium
```

Override them directly:

```bash
python agent.py \
  --mode claude \
  --model claude-sonnet-5-5 \
  --effort high \
  "Where is PKG123?"
```

Or configure them with:

```text
ANTHROPIC_MODEL
ANTHROPIC_EFFORT
ANTHROPIC_MAX_TOKENS
```

`CLAUDE_SETUP.md` contains the full runtime controls.

## Files worth showing participants

```text
agent.py
llm.py
tools.py
prompts/system.md
prompts/user.md
data/packages.json
fake_responses.json
```

The important teaching boundary remains:

> The model requests an action. Python decides whether it is allowed and executes it.
