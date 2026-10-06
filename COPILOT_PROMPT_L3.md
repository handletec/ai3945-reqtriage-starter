# Copilot/Claude Prompt — Upgrade the Working L2 Agent to L3

Use this only after the morning L2 exercise is working and `python -m pytest -q` shows `4 passed`.

Copy everything inside the block below into GitHub Copilot Chat with Claude selected.

```text
Read these files before changing anything:

- README.md
- L3_EXTENSION.md
- CONCEPTS.md
- agent.py
- tools.py
- prompts/system.md
- prompts/system_l3.md
- prompts/user.md
- fake_responses.json
- fake_responses_l3.json
- data/packages.json
- data/depots.json
- tests/test_agent.py
- verify_l3.py

Your task is to upgrade the existing working L2 agent in agent.py so the SAME program can demonstrate both L2 and L3.

Do not redesign the project and do not add an agent framework.

Keep the morning L2 behaviour working.

Required command-line interface:

python agent.py --mode copilot --level l2 "Where is PKG123?"
python agent.py --mode copilot --level l3 "My parcel PKG123 is delayed. Can I collect it from the depot today?"
python agent.py --mode fake --level l2
python agent.py --mode fake --level l3

Implement these exact authority profiles:

L2:
- allowed tools: track_package
- maximum tool actions: 1
- maximum model turns: 2
- system prompt: prompts/system.md
- fake responses: fake_responses.json

L3:
- allowed tools: track_package and get_depot_info
- maximum tool actions: 2
- maximum model turns: 3
- system prompt: prompts/system_l3.md
- fake responses: fake_responses_l3.json

Make these changes in agent.py:

1. Import get_depot_info from tools.
2. Add paths for prompts/system_l3.md and fake_responses_l3.json.
3. Add a small LEVELS configuration dictionary containing the L2 and L3 settings above.
4. Change run_agent() to:
   run_agent(request: str, llm, level: str = "l2") -> dict
5. Preserve L2 as the default so the existing morning tests still work.
6. Select the system prompt and budgets from LEVELS[level].
7. Keep a tool_history list for the whole run. Do NOT replace earlier tool results with the newest one.
8. Before every model call, render ALL tool evidence collected so far into prompts/user.md. On the first turn use "No tool has been run yet.".
9. After each successful tool call, append an entry containing the tool name and result to tool_history.
10. Before executing a requested tool:
   - check that the tool is allowed at the selected level;
   - check that tool budget remains;
   - validate the arguments.
11. Tool routing:
   - track_package requires a non-empty tracking_id string;
   - get_depot_info requires a non-empty depot_name string.
12. Execute only the selected approved Python function.
13. Continue the loop until final or the selected model-turn budget is exhausted.
14. Include level in completed and degraded results as uppercase L2 or L3.
15. Add --level with choices l2 and l3, default l2.
16. Update build_llm() so fake mode chooses the matching L2 or L3 response file.
17. Before each run print:
    AUTONOMY LEVEL: L2 or L3
    Allowed tools: ...
    Tool-action budget: ...
    Model-turn budget: ...
18. Keep --mode copilot|fake unchanged.
19. Do not change llm.py, tools.py, prompt files, data files, or tests.

After editing:

1. Show me the LEVELS dictionary.
2. Show me the updated run_agent() function.
3. Show me the tool-routing section.
4. Briefly explain what changed between L2 and L3.

Do not add shell execution, filesystem writes, retries, memory, planning frameworks, or any third tool.
```
