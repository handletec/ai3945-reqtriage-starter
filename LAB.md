# Trainer Demo Flow

This is the completed reference implementation for the simplified participant exercise.

## Demo 1 — Start with FakeLLM

Run:

```bash
python agent.py --mode fake
```

Show:

1. `prompts/system.md` — runtime rules;
2. `prompts/user.md` — request plus tool result;
3. `fake_responses.json` — deterministic model responses;
4. `agent.py` — orchestration;
5. `tools.py` — actual local action.

Point out:

```text
two model turns
one tool action
Python executes the tool
```

## Demo 2 — Switch only the runtime model

After `python model_check.py` succeeds:

```bash
python agent.py --mode claude
```

The orchestration is unchanged. Only the `llm` implementation changes.

## Demo 3 — Change model effort

```bash
python agent.py --mode claude --effort low
python agent.py --mode claude --effort medium
python agent.py --mode claude --effort high
```

Do not imply effort changes the authority boundary. It changes how much work Claude puts into the response. Python still enforces the same one-tool limit.

## Demo 4 — Different parcel

```bash
python agent.py --mode claude "Has PKG456 already been delivered?"
```

Then:

```bash
python agent.py --mode claude "Where is parcel UNKNOWN999?"
```

## Demo 5 — Run tests

```bash
python -m pytest -q
```

Expected:

```text
4 passed
```

The tests use scripted model responses so they are independent of Claude variability.
