# FakeLLM fixtures

Once you implement `FakeLLM.from_fixture_file()` (see
`reqtriage/llm/fake.py`), a fixture here is a plain JSON file shaped
like:

```json
{
  "responses": ["first scripted response text", "second scripted response text"]
}
```

This directory is intentionally empty otherwise — writing your own
fixture, with your own scripted responses, is part of validating your
`FakeLLM` implementation against something other than an inline list in
a test file.
