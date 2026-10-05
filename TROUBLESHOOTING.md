# Troubleshooting

## I cloned the repo but do not see LAB.md at the root

Run:

```bash
git branch --show-current
```

It must be:

```text
participant-guided-agent-v2
```

## `copilot` command is not found

Follow `COPILOT_SETUP.md`, then verify:

```bash
copilot --version
```

## Python package `copilot` is missing

Activate your virtual environment and run:

```bash
python -m pip install -r requirements.txt
```

## Copilot works in VS Code but `model_check.py` fails

VS Code Copilot and Copilot CLI authentication are separate surfaces.

Run:

```bash
copilot login
python model_check.py
```

Use the GitHub account that has your Copilot entitlement.

## Organization policy error

If your Copilot access is supplied by an organization, that organization must allow GitHub Copilot CLI.

Show the error to the trainer.

## Morning: `tool_not_allowed`

In L2 the only permitted runtime tool is:

```text
track_package
```

If the model requests `get_depot_info` during the morning L2 exercise, Python should reject it.

That is correct L2 behaviour.

## Morning: tests do not show `4 passed`

Do not start L3 yet.

Check that Copilot/Claude changed only `run_agent()` and followed `COPILOT_PROMPT.md`.

Run:

```bash
python -m pytest -q
```

Fix L2 until the result is:

```text
4 passed
```

## Afternoon: `run_agent()` does not accept `level=`

You have not completed the L3 upgrade yet.

Use the complete prompt in:

```text
COPILOT_PROMPT_L3.md
```

Then run:

```bash
python verify_l3.py
```

## Afternoon: `get_depot_info` is rejected in L3

Check that your L3 configuration allows both:

```text
track_package
get_depot_info
```

and that `--level l3` is actually selected.

## Afternoon: L2 stopped working after the upgrade

The L3 upgrade must preserve L2 as the default.

Run:

```bash
python -m pytest -q
```

It should still show:

```text
4 passed
```

Then run:

```bash
python verify_l3.py
```

## `JSONDecodeError` or invalid model output

Inspect the printed `MODEL TURN` response.

Do not silently turn malformed output into an empty object.

Retry once manually if using the real model. If it persists, show the raw response to the trainer.

## `tool_budget_exhausted`

The model tried to act beyond the current level's action budget.

That is a policy boundary, not a Python crash.

## FakeLLM output is always the same

That is expected.

FakeLLM is deliberately deterministic so you can test the Python control flow repeatedly.
