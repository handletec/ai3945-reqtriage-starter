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
python agent.py --mode fake --level l2
python agent.py --mode fake --level l3
```

## DNS or connection error

If Claude reports a name-resolution or connection failure, verify the container can resolve:

```bash
getent hosts api.anthropic.com
```

The agent logic can still be demonstrated with FakeLLM while the network path is repaired.

## Model not found

List models available to the current API key:

```bash
python list_models.py
```

Then select one explicitly:

```bash
python agent.py --model claude-sonnet-5-5 --level l3
```

## Effort rejected by the API

Not every model supports every effort value.

Return to the trainer default:

```bash
python agent.py --model claude-sonnet-5-5 --effort medium --level l3
```

## L2 does not answer the collection question fully

That is expected.

L2 is deliberately limited to:

```text
track_package
1 tool action
2 model turns
```

It can determine that PKG123 is at the Penang depot, but it cannot independently call `get_depot_info`.

Run the same request at L3:

```bash
python agent.py --mode fake --level l3
```

## `tool_not_allowed`

The model requested a tool outside the current level's allow-list.

At L2 only `track_package` is allowed.

At L3 `track_package` and `get_depot_info` are allowed.

Any other tool remains rejected.

## `tool_budget_exhausted`

The model requested another action after the current autonomy level's action budget was spent.

That is a policy boundary, not a Python crash.

## `invalid_model_output`

Inspect the printed `MODEL TURN` output.

The runtime model is instructed to produce JSON, but Python still validates the result instead of trusting it.

## Fake mode works but Claude mode fails

That usually points to API authentication, DNS/network access, model availability, or runtime configuration rather than the orchestration.

Run:

```bash
python check_env.py
python model_check.py
```

before changing `agent.py`.

## Tests

Run:

```bash
python -m pytest -q
```

Expected:

```text
8 passed
```

The tests cover both L2 and L3 without requiring a live Claude request.
