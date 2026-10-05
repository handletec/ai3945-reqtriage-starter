# Minimal Concepts for the L2 → L3 Lab

## One Copilot account, two different roles

### Coding assistant

GitHub Copilot Chat with Claude helps you write and later upgrade the Python.

### Runtime model

When you run:

```bash
python agent.py --mode copilot ...
```

your Python program calls the GitHub Copilot SDK.

That runtime call is separate from the Copilot Chat window that helped you write the code.

## FakeLLM

`FakeLLM` is not an AI model.

It replays scripted responses so you can repeat the same control flow exactly.

Morning L2 uses:

```text
fake_responses.json
```

Afternoon L3 uses:

```text
fake_responses_l3.json
```

## Tool

A tool is an ordinary Python function exposed through a controlled application boundary.

Morning:

```text
track_package(tracking_id)
```

Afternoon adds:

```text
get_depot_info(depot_name)
```

The model requests a tool. Python decides whether that request is allowed and performs the call.

## Model turn versus tool action

L2 normally uses:

```text
model turn 1 → request track_package
tool action 1 → Python performs lookup
model turn 2 → final answer
```

L3 may use:

```text
model turn 1 → request track_package
tool action 1 → Python performs lookup
model turn 2 → request get_depot_info
tool action 2 → Python performs lookup
model turn 3 → final answer
```

Model turns and tool actions are separate budgets.

## L2 autonomy

In this course, L2 means the model may explicitly choose **one approved action**.

Morning limits:

```text
allowed tools: track_package
tool actions: 1
model turns: 2
```

## L3 autonomy

In this course, L3 means the model may choose **multiple approved actions within explicit limits**.

Afternoon limits:

```text
allowed tools: track_package, get_depot_info
tool actions: 2
model turns: 3
```

L3 is still bounded. It does not mean the model may execute arbitrary tools.

## Same model, different authority

The key lesson is:

> L3 is not automatically a smarter model. The application gives the model more bounded authority to continue acting.

## Why Copilot SDK tools are disabled

The runtime adapter uses Copilot SDK `mode="empty"` with `available_tools=[]`.

That prevents Copilot's own shell/filesystem/coding tools from hiding the exercise.

Our model returns JSON action requests. **Our Python** validates and executes them.

## Safe degradation

A degraded result is a structured non-success result when the run cannot safely complete.

Failure is allowed. Guessing or ambiguous success is not.
