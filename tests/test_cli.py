"""CLI scaffolding tests — complete for what the CLI currently does
(load and validate a request file). Add more once the CLI calls a model
(see the TODO in `reqtriage/cli.py`)."""

from __future__ import annotations

import json
from pathlib import Path

from reqtriage.cli import main

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_exit_0_prints_the_loaded_request(capsys):
    code = main([str(REPO_ROOT / "data" / "samples" / "req_001.json")])
    assert code == 0
    output = json.loads(capsys.readouterr().out)
    assert output["request_id"] == "req_001"


def test_exit_1_on_missing_request_file():
    code = main([str(REPO_ROOT / "data" / "samples" / "does_not_exist.json")])
    assert code == 1


def test_exit_1_on_invalid_request_json(tmp_path):
    bad_file = tmp_path / "bad.json"
    bad_file.write_text("{not valid json")
    code = main([str(bad_file)])
    assert code == 1


def test_exit_1_on_request_schema_violation(tmp_path):
    bad_file = tmp_path / "bad_schema.json"
    bad_file.write_text(json.dumps({"request_id": "", "source": "ticket_form", "description": "x"}))
    code = main([str(bad_file)])
    assert code == 1


# TODO (later exercise): once the CLI calls a model, add a test that
# builds a FakeLLM with a scripted response and asserts the CLI prints
# it — see tests/test_fake_llm.py first, this depends on that exercise.
