# Trainer Reference Concepts

## The autonomy dial

This trainer uses one agent implementation with two explicit authority profiles.

### L2

```text
one approved model-selected action
one tool action maximum
two model turns maximum
allowed tool: track_package
```

### L3

```text
multiple bounded model-selected actions
two tool actions maximum
three model turns maximum
allowed tools:
- track_package
- get_depot_info
```

L3 is not defined here as unlimited autonomy. It is still tightly bounded.

## Why the same question matters

The trainer asks both levels:

```text
My parcel PKG123 is delayed. Can I collect it from the depot today?
```

L2 can discover where the parcel is but cannot independently look up collection rules.

L3 can use the result of the first action to choose a second approved action.

That makes the progression observable.

## Authority versus intelligence

Changing:

```text
--effort low
```

to:

```text
--effort high
```

changes model behaviour and reasoning effort.

Changing:

```text
--level l2
```

to:

```text
--level l3
```

changes what Python permits the agent to do.

These are different controls.

## Runtime model

`AnthropicLLM` calls Claude through the Anthropic Messages API.

FakeLLM replays scripted responses so the control flow is deterministic.

## Tool chaining

L3 demonstrates a simple dependency:

```text
track_package("PKG123")
→ returns location "Penang depot"

get_depot_info("Penang depot")
→ returns collection rules

final answer
```

The second action uses evidence produced by the first action.

## Authority boundary

The model returns a requested action as JSON.

Python then checks:

```text
Is the tool allowed at this level?
Is there tool budget left?
Are the arguments valid?
```

Only then does Python execute the function.

## Safe completion under L2

L2 should not guess collection information.

If its authority is insufficient, it should clearly state what it knows and what it cannot verify.

That is a successful bounded outcome, not a model failure.

## Safe degradation

Malformed model output, an unapproved tool, invalid arguments, or an exceeded budget returns a structured degraded result.
