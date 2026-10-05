# Trainer Reference Concepts

## Claude is the runtime model

`AnthropicLLM` in `llm.py` calls Claude through the Anthropic Messages API.

The default runtime is:

```text
claude-sonnet-5-5
medium effort
4096 max output tokens
```

## Model selection

The model is not hard-coded into the orchestration.

Choose it with:

```bash
python agent.py --model MODEL_ID
```

or:

```text
ANTHROPIC_MODEL
```

## Effort

Effort controls how much work Claude puts into the response.

The trainer exposes:

```text
low
medium
high
xhigh
max
```

Choose it with:

```bash
python agent.py --effort high
```

or:

```text
ANTHROPIC_EFFORT
```

Effort affects latency, token usage, reasoning depth, and the model's overall response behaviour. It does **not** grant additional authority to the agent.

Not every model supports every effort level.

## Thinking versus effort

Current Claude models can use adaptive thinking. Effort is the main application-level control used here to steer how much work Claude performs.

This demo does not depend on receiving or displaying Claude's thinking content. It consumes only the final text block containing our JSON action.

## Coding assistant versus runtime

The trainer branch does not require Copilot.

The program calls Claude directly at runtime.

Participants may still use Copilot/Claude in VS Code to write their own code, but that development-time assistant is separate from this trainer runtime.

## FakeLLM

`FakeLLM` replays scripted responses from `fake_responses.json`.

It is useful for deterministic demonstrations and tests:

```text
Claude   → real model judgement
FakeLLM  → predictable agent engineering
```

## Authority boundary

The model does not execute `track_package()`.

It requests:

```json
{
  "action": "call_tool",
  "tool": "track_package",
  "arguments": {
    "tracking_id": "PKG123"
  }
}
```

`agent.py` parses and validates that request.

Only then does Python execute the tool.

## L2 autonomy

This exercise permits at most one approved model-selected action.

```text
model turn 1
→ one approved tool action
→ model turn 2
→ final answer
```

The two model turns and one tool action are separate budgets.

## Safe degradation

Invalid model output, an unapproved tool, invalid arguments, or an exhausted budget returns a structured degraded result rather than guessing or silently continuing.
