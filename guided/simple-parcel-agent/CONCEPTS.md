# Concepts Used in the Simple Parcel Agent

This is a reference. You do not need to memorise it before starting the lab.

## 1. Coding assistant vs runtime model

These are different roles.

```text
Claude used in the editor
→ helps you write Python

FakeLLM / real LLM used by agent.py
→ is part of the program while it runs
```

Do not confuse "Claude wrote this code" with "the running agent called Claude".

## 2. System prompt

The system prompt defines the runtime model's job, rules, limits and allowed output.

In this lab it defines:

- one allowed tool: `track_package`;
- one tool-action maximum;
- the allowed JSON response shapes;
- the rule that parcel status must not be invented.

## 3. User prompt

The user prompt contains the actual problem to work on.

On the first model turn it contains the parcel question.

After the tool runs, the next user prompt also contains the trusted tool result so the model can finalise.

## 4. Tool

A tool is ordinary code that we wrote and exposed to the agent in a controlled way.

In this lab:

```python
track_package(tracking_id, data_path)
```

reads synthetic local data.

The model does not create this function and does not execute it directly.

## 5. Tool request vs tool execution

The model can return:

```json
{
  "action": "call_tool",
  "tool": "track_package",
  "arguments": {
    "tracking_id": "PKG123"
  }
}
```

That is only a **request**.

Python still checks:

```text
Is call_tool an allowed action?
Is track_package an allowed tool?
Is tracking_id valid?
Has the tool budget already been used?
```

Only then does Python execute the tool.

## 6. Model turn

A model turn is one call to `llm.complete(...)`.

A normal L2 run here uses two model turns:

```text
turn 1: request the tool
turn 2: finalise after seeing the tool result
```

## 7. Tool-action budget

The tool-action budget is the maximum number of tool executions allowed in one run.

This lab uses:

```text
max tool actions = 1
```

Even if the model requests a second tool call, Python must refuse it.

## 8. Why model turns and tool actions are separate

One tool call normally needs two model turns:

```text
model turn 1
→ asks for tool

tool action 1
→ Python runs tool

model turn 2
→ model finalises
```

Therefore model turns and tool actions are different counters.

## 9. FakeLLM

FakeLLM is a hand-written test double for the runtime model.

It returns scripted strings in order.

Example script:

```text
response 1 → call track_package
response 2 → final answer
```

It is useful because repeated runs receive the same model responses.

## 10. Application JSON contract

The model-output JSON shape is designed by us.

The provider's API may use a completely different envelope internally. Our adapter eventually extracts the model content and gives our agent the text it must validate.

## 11. L1, L2 and L3

For this course:

### L1

```text
model: "delivery_problem"
Python: delivery_problem → run some deterministic workflow
```

The model classifies. It does not choose the tool.

### L2

```text
model: request track_package
Python: validate and execute once
model: final answer
```

The model may choose one approved tool action.

### L3

```text
model: choose tool A
→ see result
→ choose tool B based on that result
→ see result
→ finalise
```

The model may choose a bounded sequence of tools we already wrote.

## 12. Degraded result

Failure is allowed. Silent or misleading success is not.

Instead of crashing or guessing, the agent can return something like:

```json
{
  "status": "degraded",
  "error": "tool_budget_exhausted"
}
```

That makes failure explicit and inspectable.
