# Morning Copilot/Claude Prompt — Implement L2 Only

Copy everything inside the block below into GitHub Copilot Chat with Claude selected.

```text
Read these files before changing anything:

- README.md
- LAB.md
- CONCEPTS.md
- prompts/system.md
- prompts/user.md
- data/packages.json
- tools.py
- llm.py
- fake_responses.json
- agent.py

Your task is ONLY to implement run_agent() in agent.py for the MORNING L2 exercise.

Do not redesign the project.

The repository also contains afternoon L3 files. Ignore them for this task.

Even though tools.py contains get_depot_info(), do NOT use it in L2.

The existing code already provides:
- CopilotLLM for the real GitHub Copilot runtime;
- FakeLLM for deterministic scripted responses;
- build_llm() and --mode copilot|fake;
- the L2 prompt paths;
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
6. Print each raw model response under MODEL TURN N.
7. Parse the response with the existing parse_action() helper.
8. If action == final:
   - require answer to be a non-empty string;
   - return status=completed;
   - include answer, model_turns and tool_actions.
9. If action == call_tool:
   - refuse if the one-tool budget has already been used;
   - allow ONLY track_package;
   - require arguments to be an object;
   - require arguments.tracking_id to be a non-empty string;
   - call track_package(tracking_id, PACKAGE_DATA);
   - count it as one tool action;
   - print the tool call and result under TOOL;
   - serialize the tool result to JSON;
   - use that JSON as tool_result on the next model turn.
10. If the model requests a second tool:
    - return status=degraded;
    - error=tool_budget_exhausted.
11. If the tool name is anything except track_package:
    - return status=degraded;
    - error=tool_not_allowed.
12. If required arguments are invalid:
    - return status=degraded;
    - error=invalid_tool_arguments.
13. If the model does not finalise before MAX_MODEL_TURNS:
    - return status=degraded;
    - error=model_turn_budget_exhausted.
14. Keep the function small and readable.

Do not:
- use get_depot_info;
- add L3 behaviour;
- change MAX_MODEL_TURNS;
- change MAX_TOOL_ACTIONS;
- modify prompt files;
- modify llm.py;
- modify tools.py;
- change build_llm();
- add shell execution;
- add filesystem writes;
- add retries;
- add packages;
- add an agent framework.

After editing, show me only the run_agent() implementation and a short explanation of the L2 control flow.
```
