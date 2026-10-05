# Trainer Demo Flow — L2 to L3

Use the same question throughout:

```text
My parcel PKG123 is delayed. Can I collect it from the depot today?
```

The purpose is to make the autonomy change visible without changing the architecture.

## Demo 1 — Show L2 authority

Run:

```bash
python agent.py --mode fake --level l2
```

The program announces:

```text
AUTONOMY LEVEL: L2
Allowed tools: track_package
Tool-action budget: 1
Model-turn budget: 2
```

Expected flow:

```text
MODEL TURN 1
→ track_package("PKG123")

TOOL
→ parcel is delayed
→ location is Penang depot

MODEL TURN 2
→ final answer
→ collection cannot be verified under L2
```

Ask participants:

> Did the model fail?

Answer: no. It completed correctly within the authority it was given.

## Demo 2 — Show L3 authority

Run the exact same question:

```bash
python agent.py --mode fake --level l3
```

The program announces:

```text
AUTONOMY LEVEL: L3
Allowed tools: get_depot_info, track_package
Tool-action budget: 2
Model-turn budget: 3
```

Expected flow:

```text
MODEL TURN 1
→ track_package("PKG123")

TOOL 1
→ Penang depot

MODEL TURN 2
→ get_depot_info("Penang depot")

TOOL 2
→ collection allowed
→ opening hours 09:00-18:00

MODEL TURN 3
→ final answer
```

Now ask:

> What changed?

Answer:

```text
Not the model.
Not the tool mechanism.
Not the JSON contract.
Not the Python loop.

Only the authority:
1 action → 2 actions
1 approved tool → 2 approved tools
2 turns → 3 turns
```

## Demo 3 — Show the code

Open `agent.py` and point to:

```python
LEVELS = {
    "l2": {
        "max_tool_actions": 1,
        "max_model_turns": 2,
        "allowed_tools": {"track_package"},
    },
    "l3": {
        "max_tool_actions": 2,
        "max_model_turns": 3,
        "allowed_tools": {"track_package", "get_depot_info"},
    },
}
```

This is the autonomy dial for the demonstration.

Then show `execute_tool()`.

The model does not directly execute either Python function.

## Demo 4 — Repeat with real Claude

After `python model_check.py` succeeds:

```bash
python agent.py --mode claude --level l2
```

Then:

```bash
python agent.py --mode claude --level l3
```

Real-model wording may vary. The Python authority does not.

## Demo 5 — Effort is different from autonomy

Run, for example:

```bash
python agent.py --mode claude --level l3 --effort low
python agent.py --mode claude --level l3 --effort high
```

Make the distinction explicit:

```text
effort = how much work the model puts into the response
level  = what actions Python permits the agent to take
```

Higher effort does not turn L2 into L3.

## Demo 6 — Tests

Run:

```bash
python -m pytest -q
```

Expected:

```text
8 passed
```

The tests cover:

- known and unknown package lookup;
- known and unknown depot lookup;
- L2 one-action completion;
- L3 two-action completion;
- L2 rejection of the L3-only tool;
- rejection of an unapproved tool even at L3.
