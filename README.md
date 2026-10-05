# AI3945 — Guided Copilot Agent Lab

This branch contains one hands-on agent that you will build in **two stages**.

```text
Morning   → L2 agent
Afternoon → upgrade the same working agent to L3
```

Do not try to complete both stages at once.

## The learning sequence

### Morning — L2

You build a parcel agent that may select **one approved action**:

```text
track_package
```

Use:

```text
LAB.md
COPILOT_PROMPT.md
```

Complete L2 and reach:

```text
4 passed
```

before starting the afternoon extension.

### Afternoon — L3

You upgrade the same agent so it can perform a second bounded action when needed:

```text
track_package
→ get_depot_info
→ final answer
```

Use:

```text
L3_EXTENSION.md
COPILOT_PROMPT_L3.md
```

The goal is to see that L3 is the same basic agent loop with more bounded authority—not a different architecture.

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

## 2. Repository root

You should see:

```text
README.md
LAB.md
L3_EXTENSION.md
COPILOT_SETUP.md
COPILOT_PROMPT.md
COPILOT_PROMPT_L3.md
CONCEPTS.md
TROUBLESHOOTING.md
agent.py
llm.py
tools.py
check_env.py
model_check.py
verify_l3.py
fake_responses.json
fake_responses_l3.json
requirements.txt
prompts/
data/
tests/
```

Some L3 files are already present so you do not need to download another starter in the afternoon.

**Ignore the L3 files during the morning exercise.**

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

## 4. Set up Copilot runtime access

Read:

```text
COPILOT_SETUP.md
```

Then run:

```bash
python check_env.py
python model_check.py
```

Do not start the coding exercise until `model_check.py` succeeds.

## 5. Begin with L2

Open:

```text
LAB.md
```

Follow it from top to bottom.

When the trainer starts the L3 section later, open:

```text
L3_EXTENSION.md
```

Do not skip ahead.
