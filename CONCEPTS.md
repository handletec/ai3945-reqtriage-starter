# Minimal Concepts for This Lab

## One Copilot account, two different roles

### 1. Coding assistant

GitHub Copilot Chat with Claude in VS Code helps you write `run_agent()`.

That happens while you are developing the program.

### 2. Runtime model

When you run:

```bash
python agent.py --mode copilot ...
```

your Python program calls the GitHub Copilot SDK.

The SDK uses the GitHub identity you signed in with through Copilot CLI.

This is a runtime model call made by your program. It is separate from the Copilot Chat window that helped you write the code.

## FakeLLM

`FakeLLM` is not an AI model.

It returns scripted responses from `fake_responses.json`.

We use it after the real-model run so we can repeat the exact same agent behaviour during testing.

```text
real Copilot runtime → experience real model behaviour
FakeLLM             → test the Python machinery predictably
```

## System prompt

`prompts/system.md` gives the runtime model its role, allowed action, limits, and JSON output contract.

## User prompt

`prompts/user.md` carries the current user request and, after a lookup, the tool result.

## Tool

`track_package()` is an ordinary Python function.

The runtime model may **request** that tool.

Your Python decides whether the request is allowed and performs the call.

## Why Copilot SDK tools are disabled

The runtime adapter uses Copilot SDK `mode="empty"` with `available_tools=[]`.

That prevents Copilot's own shell/filesystem/coding tools from hiding the lesson.

The model returns our JSON action. **Our Python** validates and executes it.

## Model turn versus tool action

A normal run uses:

```text
model turn 1 → request track_package
tool action 1 → Python performs lookup
model turn 2 → final answer
```

Two model turns does not mean two tool actions.

## L2 autonomy

For this course, L2 means the model may explicitly choose **one approved action**.

Python still validates and executes it.

## Degraded result

A degraded result is a structured non-success result when the run cannot safely complete.

Failure is allowed. Guessing or ambiguous success is not.
