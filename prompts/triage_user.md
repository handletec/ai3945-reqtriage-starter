<!-- prompt_version: v1-template -->
Here is the incoming request:

```json
<<REQUEST_JSON>>
```

Tool results so far this run (empty if none yet):

```json
<<TOOL_RESULTS_JSON>>
```

Respond with exactly one JSON object as described in the system prompt:
either a `call_tool` action or a `final` action.
