from __future__ import annotations

import dataclasses
import json
from pathlib import Path

import pytest

from reqtriage.config import Settings
from reqtriage.models import TriageRequest

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURES_DIR = REPO_ROOT / "tests" / "fixtures" / "llm_responses"


@pytest.fixture()
def settings(tmp_path: Path) -> Settings:
    """The real repo settings, EXCEPT `logging.log_path` is redirected
    into pytest's per-test `tmp_path`.

    Without this, every test that calls `run_triage` would append to the
    real `logs/runs.jsonl` in the repository — polluting the shipped
    checkout with generated data every time the suite runs, and making a
    "clean" release zip depend on remembering to delete it afterwards.
    Redirecting here fixes the cause once, for every test, rather than
    relying on manual cleanup before packaging.
    """

    base = Settings.load(repo_root=REPO_ROOT)
    return dataclasses.replace(
        base, logging=dataclasses.replace(base.logging, log_path=tmp_path / "runs.jsonl")
    )


@pytest.fixture()
def make_settings(settings: Settings):
    """Build a variant of the (already log-isolated) test settings with a
    different autonomy budget, for tests that need to exercise a
    specific L1/L2/L3 configuration explicitly rather than the repo's
    default. Usage: `make_settings(max_tool_actions=1, max_model_turns=3)`.
    """

    def _make(*, max_tool_actions: int | None = None, max_model_turns: int | None = None) -> Settings:
        agent = settings.agent
        if max_tool_actions is not None:
            agent = dataclasses.replace(agent, max_tool_actions=max_tool_actions)
        if max_model_turns is not None:
            agent = dataclasses.replace(agent, max_model_turns=max_model_turns)
        return dataclasses.replace(settings, agent=agent)

    return _make


@pytest.fixture()
def make_request():
    def _make(**overrides):
        defaults = dict(
            request_id="req_test",
            source="ticket_form",
            description="Something needs triage.",
        )
        defaults.update(overrides)
        return TriageRequest.model_validate(defaults)

    return _make


def load_sample(request_id: str) -> TriageRequest:
    """Load one of the placeholder request files under `data/samples/`."""

    path = REPO_ROOT / "data" / "samples" / f"{request_id}.json"
    raw = json.loads(path.read_text(encoding="utf-8"))
    return TriageRequest.model_validate(raw)


def fixture_path(name: str) -> Path:
    return FIXTURES_DIR / f"{name}.json"
