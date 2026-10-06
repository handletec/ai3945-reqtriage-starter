# Afternoon Extension — Upgrade L2 to L3

## Start only after the morning L2 checkpoint is complete

Before continuing, your morning agent must already work.

Run:

```bash
python -m pytest -q
```

Expected:

```text
4 passed
```

If you do not have `4 passed`, fix L2 first. Do not start L3 yet.

Optional but recommended: save your working morning checkpoint locally:

```bash
git add agent.py
git commit -m "Complete L2 parcel agent"
```

That gives you an easy point to compare against later.

---

## L3 goal

In the morning the agent answered:

> Where is PKG123?

with one approved action:

```text
track_package
```

In the afternoon the question becomes:

> My parcel PKG123 is delayed. Can I collect it from the depot today?

One lookup is no longer enough.

The intended L3 flow is:

```text
user request
→ model turn 1
→ track_package("PKG123")
→ parcel result says Penang depot
→ model turn 2
→ get_depot_info("Penang depot")
→ depot collection result
→ model turn 3
→ final answer
```

Python still decides whether every requested action is allowed.

For L3, the agent must also preserve the evidence from **both** tool calls. The third model turn needs to see the parcel result and the depot result together; do not overwrite the first result when the second tool runs.

---

## Checkpoint L3-1 — Inspect the new supplied pieces

Open:

```text
data/depots.json
prompts/system_l3.md
fake_responses_l3.json
tools.py
```

Do not edit them.

Notice that `tools.py` now contains a second ordinary Python function:

```text
get_depot_info(depot_name)
```

The function was supplied for the afternoon exercise. It was not needed in the morning.

---

## Checkpoint L3-2 — Run the new tool directly

Run:

```bash
python tools.py depot "Penang depot"
```

Expected evidence includes:

```json
{
  "found": true,
  "depot_name": "Penang depot",
  "collection_allowed": true,
  "opening_hours": "09:00-18:00"
}
```

This is still just normal deterministic Python.

---

## Checkpoint L3-3 — Compare the authority

Morning L2:

```text
allowed tools: track_package
tool-action budget: 1
model-turn budget: 2
```

Afternoon L3:

```text
allowed tools: track_package, get_depot_info
tool-action budget: 2
model-turn budget: 3
```

Important:

> L3 is not a different model. The same application gives the model more bounded authority to continue acting.

---

## Checkpoint L3-4 — Ask Copilot/Claude to upgrade your working code

Open:

```text
COPILOT_PROMPT_L3.md
```

Copy the complete prompt into Copilot Chat with Claude selected.

Let it modify only `agent.py`.

Inspect the diff before running it.

You should be able to identify:

1. the L2 and L3 configuration;
2. where `--level` is parsed;
3. where the selected tool allow-list is checked;
4. where the selected tool budget is checked;
5. where `track_package()` is routed;
6. where `get_depot_info()` is routed;
7. why the same loop can now perform one or two actions depending on level.

---

## Checkpoint L3-5 — Prove L2 still works

First run the old deterministic path:

```bash
python agent.py --mode fake --level l2 "Where is PKG123?"
```

Then:

```bash
python -m pytest -q
```

Expected:

```text
4 passed
```

If the morning tests broke, your upgrade changed too much. Fix L2 before continuing.

---

## Checkpoint L3-6 — Run deterministic L3

Run:

```bash
python agent.py --mode fake --level l3 \
  "My parcel PKG123 is delayed. Can I collect it from the depot today?"
```

Expected pattern:

```text
AUTONOMY LEVEL: L3
Allowed tools: get_depot_info, track_package
Tool-action budget: 2
Model-turn budget: 3

MODEL TURN 1
→ track_package

TOOL
→ Penang depot

MODEL TURN 2
→ get_depot_info

TOOL
→ collection allowed, 09:00-18:00

MODEL TURN 3
→ final
```

---

## Checkpoint L3-7 — Run the L3 verifier

Run:

```bash
python verify_l3.py
```

Expected final line:

```text
L3 verification passed.
```

This checks both levels:

- L2 still uses one approved action;
- L3 can use two approved actions;
- L2 rejects the L3-only depot tool;
- the depot tool returns expected data.

---

## Checkpoint L3-8 — Run real Copilot

Run L2 first:

```bash
python agent.py --mode copilot --level l2 \
  "My parcel PKG123 is delayed. Can I collect it from the depot today?"
```

Then L3:

```bash
python agent.py --mode copilot --level l3 \
  "My parcel PKG123 is delayed. Can I collect it from the depot today?"
```

Compare the two results.

L2 may establish the parcel location but cannot use the depot lookup.

L3 can chain the second approved action and answer from the additional evidence.

---

## Checkpoint L3-9 — Explain the difference

Be able to answer:

1. Did we change the runtime model between L2 and L3?
2. What authority did L3 gain?
3. Who chose the second tool?
4. Who actually executed the second tool?
5. Why does L3 have three model turns but only two tool actions?
6. Could L3 suddenly call `delete_package`?
7. Why are action budgets still important when the model is capable?

If you can answer those from the code you ran, the L3 extension is complete.
