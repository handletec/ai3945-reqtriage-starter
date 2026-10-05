# Minimal Concepts for This Lab

## Coding assistant

GitHub Copilot with Claude helps you write the Python.

It is development-time tooling.

## Runtime model

The Python program calls Claude through the Anthropic API while the program is running.

That is a separate connection and requires runtime credentials.

## System prompt

Rules, role, allowed tool and required output format.

## User prompt

The actual request being processed, plus the tool result after a lookup.

## Tool

A normal Python function that the application exposes in a controlled way.

The model requests a tool. Python decides whether that request may execute.

## Model turn

One call to the runtime model.

A normal run here uses:

```text
model turn 1 → request tool
tool action 1 → Python runs lookup
model turn 2 → final answer
```

## L2 autonomy

For this course, L2 means the model may explicitly choose **one approved action**.

Python still validates and executes it.

## Degraded result

A structured non-success result when the run cannot safely complete.

Failure is allowed. Guessing or ambiguous success is not.
