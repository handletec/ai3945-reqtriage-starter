# AI3945 — Guided Copilot Agent Lab

This branch is the self-contained hands-on starter for the simplified agent lab.

You are expected to know basic Python and VS Code. You are **not** expected to already understand agent architecture.

You will use GitHub Copilot in two different ways:

1. **Copilot Chat with Claude in VS Code** helps you write the missing Python.
2. **GitHub Copilot SDK** is the real runtime model connection used by the Python agent.

The same GitHub Copilot entitlement can support both. **No Anthropic API key is required for the normal lab path.**

## 1. Clone the correct branch

```bash
git clone --branch participant-guided-agent-v2 --single-branch https://github.com/handletec/ai3945-reqtriage-starter.git
cd ai3945-reqtriage-starter
```

Verify:

```bash
git branch --show-current
```

Expected:

```text
participant-guided-agent-v2
```

## 2. What should be at the repository root

```text
README.md
LAB.md
COPILOT_SETUP.md
COPILOT_PROMPT.md
CONCEPTS.md
TROUBLESHOOTING.md
agent.py
llm.py
tools.py
check_env.py
model_check.py
fake_responses.json
requirements.txt
prompts/
data/
tests/
```

If these are not at the repository root, stop. You are on the wrong branch.

## 3. Create the Python environment

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Windows PowerShell

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## 4. Set up your Copilot runtime access

Read:

```text
COPILOT_SETUP.md
```

You will install/sign in to Copilot CLI with the GitHub account that already has your Copilot entitlement.

Then run:

```bash
python check_env.py
python model_check.py
```

Do not begin the coding checkpoint until `model_check.py` succeeds.

## 5. Start the hands-on

Open:

```text
LAB.md
```

The lab gives you the exact file, action, Copilot prompt, command, expected observation, and first recovery path for each checkpoint.

## Runtime modes

After you implement `run_agent()` the same agent can run in two modes:

```bash
python agent.py --mode copilot "My parcel PKG123 was due yesterday. Where is it?"
```

uses your real GitHub Copilot account at runtime.

```bash
python agent.py --mode fake "My parcel PKG123 was due yesterday. Where is it?"
```

uses deterministic scripted responses from `fake_responses.json`.

Use the real model to experience the agent. Use FakeLLM afterwards to understand repeatable testing.
