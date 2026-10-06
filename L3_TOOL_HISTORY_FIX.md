# L3 Repair — Preserve Tool History Across Model Turns

Use this only if your L3 agent already works through both tool calls but finishes with:

```json
{
  "status": "degraded",
  "level": "L3",
  "error": "tool_budget_exhausted",
  "model_turns": 3,
  "tool_actions": 2
}
```

The likely cause is that your agent keeps only the most recent tool result. By model turn 3, the earlier `track_package()` evidence has been lost, so the model may ask for that lookup again.

## Apply the repair with Copilot/Claude

Copy everything inside the block below into GitHub Copilot Chat with Claude selected.

```text
You are fixing an already-implemented L3 parcel agent.

Do NOT redesign the project.
Do NOT rewrite the agent from scratch.
Do NOT change the autonomy levels, tool limits, prompts, tools, tests, or runtime adapter unless required for this specific fix.

Problem:

The L3 agent can successfully perform:

1. track_package(...)
2. get_depot_info(...)

but on model turn 3 it may request track_package again and return:

{
  "status": "degraded",
  "level": "L3",
  "error": "tool_budget_exhausted",
  "model_turns": 3,
  "tool_actions": 2
}

Cause:

The current implementation keeps only the most recent tool result.

After get_depot_info() runs, the earlier track_package() evidence is lost.

The third model turn therefore does not see all previous evidence and may repeat an earlier lookup.

Fix only this state-management problem.

Required change in agent.py:

1. In run_agent(), replace the single current tool-result state with:

   tool_history: list[dict] = []

2. Before every model call, build the value passed into render_user_prompt() like this:

   tool_result = (
       "No tool has been run yet."
       if not tool_history
       else json.dumps(tool_history, indent=2)
   )

3. After each successful tool execution, append the tool name and its result:

   tool_history.append({
       "tool": tool_name,
       "result": tool_output,
   })

4. Do NOT overwrite previous tool evidence.

5. By model turn 3 in L3, the model must receive evidence from BOTH:

   - track_package
   - get_depot_info

6. Preserve all existing behaviour:

   L2:
   - track_package only
   - maximum 1 tool action
   - maximum 2 model turns

   L3:
   - track_package and get_depot_info
   - maximum 2 tool actions
   - maximum 3 model turns

7. Preserve all existing validation:
   - allowed-tool checks
   - tool budget
   - model-turn budget
   - argument validation
   - structured degraded results

8. Do not add:
   - another tool
   - retries
   - memory frameworks
   - agent frameworks
   - shell execution
   - filesystem writes

After making the change:

1. Show me the modified section of run_agent().
2. Explain in 2-3 sentences why tool_history fixes the L3 failure.
3. Run:

   python -m pytest -q

4. Run:

   python verify_l3.py

5. Run:

   python agent.py --mode fake --level l3 \
     "My parcel PKG123 is delayed. Can I collect it from the depot today?"

Expected L3 behaviour:

MODEL TURN 1
→ track_package

TOOL 1
→ parcel is at Penang depot

MODEL TURN 2
→ get_depot_info

TOOL 2
→ collection information

MODEL TURN 3
→ final answer

The final result should be completed with:

model_turns = 3
tool_actions = 2
```

## What this repair changes

It changes only how tool evidence is carried forward between model turns. The L2/L3 authority limits remain exactly the same.
