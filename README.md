# AI3945 — Guided Real-Model Agent Lab

This branch is a self-contained hands-on starter.

You are expected to know basic Python and VS Code. You are **not** expected to already know how AI agents work.

You will use **GitHub Copilot with Claude as your coding assistant**. The Python program you build will separately call a **real Claude model at runtime**.

## 1. Clone this branch

```bash
git clone --branch participant-guided-agent-v2 --single-branch https://github.com/handletec/ai3945-reqtriage-starter.git
cd ai3945-reqtriage-starter
```

You should immediately see:

```text
README.md
LAB.md
COPILOT_PROMPT.md
MODEL_SETUP.md
CONCEPTS.md
TROUBLESHOOTING.md
agent.py
llm.py
tools.py
check_env.py
model_check.py
requirements.txt
prompts/
data/
tests/
```

If those files are not at the repository root, stop. You are on the wrong branch.

## 2. Check your starting environment

Run:

```bash
python check_env.py
```

It will tell you what is missing.

## 3. Create a Python environment

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

## 4. Configure the runtime model

Read `MODEL_SETUP.md`.

You will need the runtime credentials supplied by the trainer.

Then run:

```bash
python check_env.py
python model_check.py
```

Do not start the coding checkpoint until both succeed.

## 5. Start the hands-on

Open:

```text
LAB.md
```

The lab tells you exactly:

- what file to inspect;
- what concept you are looking at;
- what command to run;
- what prompt to give Copilot/Claude;
- what output to expect;
- how to know the step worked.

Do not ask Copilot to build a different architecture. The point is to understand this small agent loop.
