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

If not, clone the correct branch exactly as shown in `README.md`.

## `copilot` command is not found

Install GitHub Copilot CLI using `COPILOT_SETUP.md`.

Examples:

### Windows

```powershell
winget install GitHub.Copilot
```

### macOS / Linux with Homebrew

```bash
brew install --cask copilot-cli
```

Then verify:

```bash
copilot --version
```

## Python package `copilot` is missing

Activate your virtual environment and run:

```bash
python -m pip install -r requirements.txt
```

Then rerun:

```bash
python check_env.py
```

## Copilot works in VS Code but `model_check.py` fails

VS Code Copilot and Copilot CLI authentication are separate surfaces.

Run:

```bash
copilot login
```

Complete the GitHub OAuth login using the GitHub account that has your Copilot entitlement.

Then retry:

```bash
python model_check.py
```

## Access denied or organization policy error

If your Copilot access is supplied by an organization, that organization must allow GitHub Copilot CLI.

This cannot be fixed in the Python code. Show the error to the trainer.

## Wrong GitHub account

Run `copilot login` again with the account that has Copilot access.

Also check whether `COPILOT_GITHUB_TOKEN`, `GH_TOKEN`, or `GITHUB_TOKEN` is set in your shell, because an environment token can override stored login credentials.

## `model_check.py` reports no authentication information

Run:

```bash
copilot login
```

Then retry `python model_check.py`.

## `model_check.py` cannot reach the service

Confirm your machine has Internet access and that your network allows GitHub Copilot.

If FakeLLM works but Copilot mode does not, the agent code may be fine and the problem may be authentication/network access.

## `python agent.py --mode fake ...` fails before contacting a model

Fake mode does not require a live model request, but the Python dependencies still need to be installed.

Run:

```bash
python check_env.py
```

Fix any failed local checks.

## `JSONDecodeError` when running Copilot mode

The real model returned text that was not valid JSON.

Inspect the printed `MODEL TURN` output.

Do not silently convert bad output to `{}` or `None`.

For the class exercise, retry the command once manually. If the same problem persists, show the raw model response to the trainer.

## `tool_not_allowed`

Your Python correctly rejected a tool outside the allow-list.

The only permitted tool is:

```text
track_package
```

## `tool_budget_exhausted`

The runtime model requested another tool after the single permitted tool action had already been used.

That is the intended L2 authority boundary.

## Tests fail after Copilot Chat edits `agent.py`

Check that Copilot/Claude changed only `run_agent()`.

Compare the implementation with `COPILOT_PROMPT.md`.

Do not ask Copilot to redesign the project or introduce an agent framework.

## FakeLLM output is always the same

That is expected.

`FakeLLM` replays `fake_responses.json`. It exists so the engineering path can be repeated predictably.
