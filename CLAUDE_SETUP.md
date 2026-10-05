# Claude Runtime Setup

This trainer branch calls Claude directly through the Anthropic API.

## 1. API key

Set your key in the shell before starting the demo.

macOS / Linux:

```bash
export ANTHROPIC_API_KEY="your-key"
```

PowerShell:

```powershell
$env:ANTHROPIC_API_KEY="your-key"
```

Do not put the API key in source code.

## 2. Default runtime

The trainer build defaults to:

```text
model:      claude-sonnet-5-5
effort:     medium
max_tokens: 4096
```

For this small, well-specified two-turn agent, `medium` is a sensible balance of latency, cost, and reasoning depth.

## 3. Choose a model

First list what your API key can use:

```bash
python list_models.py
```

Then choose one of the returned model IDs.

CLI:

```bash
python agent.py --model claude-sonnet-5-5 "Where is PKG123?"
```

Environment:

```bash
export ANTHROPIC_MODEL="claude-sonnet-5-5"
python agent.py
```

Any model ID you choose must be available to your Anthropic API account.

## 4. Choose effort

Supported values in this trainer:

```text
low
medium
high
xhigh
max
```

CLI:

```bash
python agent.py --effort high "Where is PKG123?"
```

Environment:

```bash
export ANTHROPIC_EFFORT="high"
python agent.py
```

Not every Claude model supports every effort value. If the selected model does not support the requested effort, the Anthropic API will reject the request.

## 5. Change max output tokens

CLI:

```bash
python agent.py --max-tokens 8192
```

Environment:

```bash
export ANTHROPIC_MAX_TOKENS="8192"
```

`max_tokens` is a hard output limit. Thinking, when active for the chosen model, also counts against that limit.

## 6. Verify the API before class

```bash
python check_env.py
python model_check.py
```

Expected pattern:

```text
Connecting to Claude (model=claude-sonnet-5-5, effort=medium, max_tokens=4096)...
Model responded: READY
Claude runtime connection works.
```

## 7. FakeLLM remains available

Fake mode requires no API call:

```bash
python agent.py --mode fake --level l2
python agent.py --mode fake --level l3
```

Use it to show the same orchestration with deterministic model responses.

## 8. Autonomy level is separate from model effort

Use:

```bash
python agent.py --mode claude --level l2
python agent.py --mode claude --level l3
```

`--level` changes the Python authority boundary.

`--effort` changes how much work Claude puts into its response.

Higher effort does not grant additional tools or tool actions.
