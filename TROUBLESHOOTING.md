# Trainer Troubleshooting

## `ANTHROPIC_API_KEY` is missing

Set it before real Claude mode:

```bash
export ANTHROPIC_API_KEY="your-key"
```

Then:

```bash
python model_check.py
```

Fake mode does not make an API request:

```bash
python agent.py --mode fake
```

## Authentication error

Verify that the API key is valid and is an Anthropic API credential.

Do not paste the key into `agent.py` or `llm.py`.

## Model not found

Check the selected model:

```bash
echo "$ANTHROPIC_MODEL"
```

or run explicitly:

```bash
python agent.py --model claude-sonnet-5-5
```

The model must be available to the API account.

## Effort rejected by the API

Not every model supports every effort level.

Return to the trainer default:

```bash
python agent.py --model claude-sonnet-5-5 --effort medium
```

## Response stops early

Increase the output limit:

```bash
python agent.py --max-tokens 8192
```

The default 4096 is intentionally modest because this agent should return very small JSON actions.

## `JSONDecodeError` or `invalid_model_output`

Inspect the printed `MODEL TURN` output.

The system prompt requires one JSON object, but real models can still return malformed or unexpected text.

Do not silently convert invalid output to an empty object. The structured degraded result is the correct safe behaviour.

## `tool_not_allowed`

The model requested something other than:

```text
track_package
```

Python rejected it as intended.

## `tool_budget_exhausted`

The model attempted another tool after the one permitted action.

That is the intended L2 limit.

## Fake mode works but Claude mode fails

That usually points to API authentication, network access, model availability, or runtime configuration rather than the orchestration itself.

Run:

```bash
python check_env.py
python model_check.py
```

before debugging `run_agent()`.

## Tests

Run:

```bash
python -m pytest -q
```

Expected:

```text
4 passed
```

The tests do not require a live Claude request.
