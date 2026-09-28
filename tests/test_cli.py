"""CLI exit-code contract (see cli.py's module docstring for the table).

These call `cli.main()` directly (fast, in-process) rather than
spawning a subprocess for every case; one subprocess-based test at the
end checks the real `python -m reqtriage` invocation end-to-end.

Every invocation below passes `--log-path` into a pytest `tmp_path`.
Without it, running this file would append to the real
`logs/runs.jsonl` in the checked-out repository on every test run — see
`tests/conftest.py`'s `settings` fixture docstring for why that is a
real problem (a "clean" release zip should not depend on remembering to
delete a file these tests generated).
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from reqtriage.cli import main

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_exit_0_on_normal_result(tmp_path, capsys):
    code = main(
        [str(REPO_ROOT / "data" / "samples" / "example_001.json"), "--log-path", str(tmp_path / "runs.jsonl")]
    )
    assert code == 0
    output = json.loads(capsys.readouterr().out)
    assert output["error"] is None


def test_exit_2_on_degraded_result(tmp_path, capsys):
    bad_file = tmp_path / "empty_description.json"
    bad_file.write_text(
        json.dumps({"request_id": "empty-desc-test", "source": "ticket_form", "description": "   "})
    )
    code = main([str(bad_file), "--log-path", str(tmp_path / "runs.jsonl")])
    assert code == 2
    output = json.loads(capsys.readouterr().out)
    assert output["error"] == "missing_description"


def test_exit_1_on_missing_request_file(tmp_path, capsys):
    code = main(
        [
            str(REPO_ROOT / "data" / "samples" / "does_not_exist.json"),
            "--log-path", str(tmp_path / "runs.jsonl"),
        ]
    )
    assert code == 1


def test_exit_1_on_invalid_request_json(tmp_path, capsys):
    bad_file = tmp_path / "bad.json"
    bad_file.write_text("{not valid json")
    code = main([str(bad_file), "--log-path", str(tmp_path / "runs.jsonl")])
    assert code == 1


def test_exit_1_on_request_schema_violation(tmp_path, capsys):
    bad_file = tmp_path / "bad_schema.json"
    bad_file.write_text(json.dumps({"request_id": "", "source": "ticket_form", "description": "x"}))
    code = main([str(bad_file), "--log-path", str(tmp_path / "runs.jsonl")])
    assert code == 1


def test_exit_1_when_max_model_turns_not_greater_than_max_tool_actions(tmp_path, capsys):
    code = main(
        [
            str(REPO_ROOT / "data" / "samples" / "example_001.json"),
            "--max-tool-actions", "3",
            "--max-model-turns", "3",
            "--log-path", str(tmp_path / "runs.jsonl"),
        ]
    )
    assert code == 1


def test_max_tool_actions_override_still_succeeds(tmp_path, capsys):
    # The "example" scenario never asks for a tool at all — an override
    # that raises the ceiling must not break a run that never spends it.
    code = main(
        [
            str(REPO_ROOT / "data" / "samples" / "example_001.json"),
            "--max-tool-actions", "1",
            "--max-model-turns", "3",
            "--log-path", str(tmp_path / "runs.jsonl"),
        ]
    )
    assert code == 0
    output = json.loads(capsys.readouterr().out)
    assert output["error"] is None
    assert output["meta"]["tool_actions_used"] == 0


def test_log_path_override_is_honoured_and_default_log_is_untouched(tmp_path, capsys):
    custom_log = tmp_path / "custom_runs.jsonl"
    default_log = REPO_ROOT / "logs" / "runs.jsonl"
    default_log_existed_before = default_log.is_file()
    default_log_size_before = default_log.stat().st_size if default_log_existed_before else None

    code = main([str(REPO_ROOT / "data" / "samples" / "example_002.json"), "--log-path", str(custom_log)])
    assert code == 0
    assert custom_log.is_file()
    assert json.loads(custom_log.read_text().splitlines()[0])["request_id"] == "example_002"

    # The real repo log must be exactly as it was before this test ran.
    if default_log_existed_before:
        assert default_log.stat().st_size == default_log_size_before
    else:
        assert not default_log.is_file()


def test_real_subprocess_invocation_end_to_end(tmp_path):
    log_path = tmp_path / "runs.jsonl"
    result = subprocess.run(
        [sys.executable, "-m", "reqtriage", "data/samples/example_001.json", "--log-path", str(log_path)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert output["request_id"] == "example_001"
    assert output["error"] is None
    assert log_path.is_file()  # confirms logging happened, but into an isolated path
