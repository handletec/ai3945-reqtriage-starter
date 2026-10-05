# Copilot/Claude Prompt — Implement the Agent Loop

Copy everything inside the block below into GitHub Copilot Chat with Claude selected.

```text
Read these files before changing anything:

- README.md
- LAB.md
- prompts/system.md
- prompts/user.md
- data/packages.json
- tools.py
- llm.py
- agent.py

Your task is ONLY to implement run_agent() in agent.py.

Do not redesign the project.

The existing code already provides:
- the real Anthropic model adapter;
- prompt paths;
- the local track_package tool;
- JSON parsing;
- command-line handling;
- MAX_MODEL_TURNS = 2;
- MAX_TOOL_ACTIONS = 1.

Implement this exact L2 flow:

1. Read the system prompt from prompts/system.md.
2. Start with tool_result = "No tool has been run yet."
3. Render prompts/user.md with the request and current tool_result.
4. Call llm.complete(system, rendered_user_prompt).
5. Count each llm.complete call as one model turn.
6. Parse the returned action using the existing parse_action() helper.
7. If action == final:
   - return status=completed;
   - include answer, model_turns and tool_actions.
8. If action == call_tool:
   - refuse if the one-tool budget has already been used;
   - allow only the tool name track_package;
   - require arguments.tracking_id to be a non-empty string;
   - call track_package(tracking_id, PACKAGE_DATA);
   - count it as one tool action;
   - serialize the tool result to JSON;
   - send that result back to the model on the next turn.
9. If the model does not finalise before MAX_MODEL_TURNS:
   - return status=degraded;
   - error=model_turn_budget_exhausted.
10. For rejected authority or validation cases, return a structured degraded result.
11. Keep the function small and readable.

For the live demonstration, print:
- each raw model response as MODEL TURN N;
- the tool call and tool result under TOOL.

Do not:
- add another tool;
- add L3 behaviour;
- add shell execution;
- add filesystem write actions;
- change prompts;
- change llm.py;
- change tools.py;
- change the budgets;
- add retries;
- add packages.

After editing, show me only the run_agent() implementation and a short explanation of the control flow.
```
