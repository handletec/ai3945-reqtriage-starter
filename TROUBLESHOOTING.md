# Troubleshooting

## I cloned the repo but do not see LAB.md at the root

Check:

```bash
git branch --show-current
```

It must be:

```text
participant-guided-agent-v2
```

If not, clone the correct branch as shown in README.md.

## check_env.py says a package is missing

Activate your virtual environment and run:

```bash
python -m pip install -r requirements.txt
```

Then rerun:

```bash
python check_env.py
```

## check_env.py says .env is missing

Create it from the example:

```bash
cp .env.example .env
```

On PowerShell:

```powershell
Copy-Item .env.example .env
```

Then add the credentials supplied by the trainer.

## My Copilot Claude works but model_check.py fails

These are separate systems.

Copilot/Claude is your coding assistant.

`model_check.py` uses the Anthropic API from your Python program and needs the runtime API key and model name supplied by the trainer.

## Authentication error

Check `ANTHROPIC_API_KEY` in `.env`.

Do not paste the key into source code.

## Model not found / invalid model

Check `ANTHROPIC_MODEL` in `.env` against the model name supplied by the trainer.

## JSONDecodeError when running agent.py

The real model returned text that was not valid JSON.

First inspect the printed MODEL TURN output.

Do not silently replace invalid output with `{}` or `None`.

For the core lab, retry once manually. If it persists, show the trainer the raw model response.

## tool_not_allowed

Your Python correctly rejected a tool name outside the allow-list.

The only permitted tool is `track_package`.

## tool_budget_exhausted

The model requested another tool after the single allowed tool action was already used.

That is a safe L2 boundary.

## Tests fail after Copilot edits agent.py

Check that Copilot changed only `run_agent()`.

Compare your implementation with the exact requirements in `COPILOT_PROMPT.md`.
