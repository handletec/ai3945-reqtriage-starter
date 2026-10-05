# Troubleshooting — Simple Parcel Agent

Use this only after reading the error. Do not immediately ask Claude to rewrite the whole lab.

## `python check_env.py` says pytest is missing

Activate the lab virtual environment, then run:

```bash
python -m pip install -r requirements.txt
python check_env.py
```

## `python agent.py --mode fake` prints only the starter message

That is expected before Checkpoint 2.

Open `LAB.md` and use the Checkpoint 2 Claude prompt to implement `agent.py`.

## `FileNotFoundError` for prompts or data

Run commands from the directory containing:

```text
README.md
LAB.md
agent.py
prompts/
data/
```

Check with:

```bash
python check_env.py
```

## `JSONDecodeError`

The model response could not be parsed as JSON.

For the FakeLLM path, inspect `fake_responses.json`. Each response must be a JSON string containing one valid action object.

Do not fix this by silently returning `{}` or `None`.

## `tool_not_allowed`

Python rejected a tool name that is not on the allow-list.

This is the correct safe behaviour for something like:

```text
delete_package
```

The only tool permitted by this lab is:

```text
track_package
```

## `tool_budget_exhausted`

The model requested another tool after the one allowed tool action was already used.

This is expected in the negative budget test.

L2 in this lab permits one tool action only.

## The tool returns `found: false`

That is a normal lookup miss, not necessarily a tool failure.

It means the lookup executed correctly but no parcel matched the tracking ID.

Do not invent a parcel status to fill the missing value.

## Tests cannot import `agent`

Make sure you run pytest from this lab directory:

```bash
python -m pytest -q
```

Do not run the tests while your shell is inside the `tests/` directory.

## Real-model mode fails because environment variables are missing

Real-model mode is optional.

Finish the FakeLLM checkpoints first.

For the optional real adapter you need:

```text
LLM_URL
LLM_MODEL
LLM_API_KEY    (only if your endpoint requires it)
```

## Real model returns Markdown fences around JSON

That is model-behaviour variability. The simple guided lab intentionally expects the model to follow the system prompt and return raw JSON.

Do not redesign the whole agent during the core lab. First prove the deterministic FakeLLM path.

## Claude changes unrelated files

Reject or revert the unrelated changes.

The checkpoint prompt is intentionally bounded. Ask Claude to modify only the files named by that checkpoint.

## I am unsure whether the bug is the model or my code

Return to FakeLLM.

If the failure reproduces with the same scripted FakeLLM responses, debug the Python path first.
