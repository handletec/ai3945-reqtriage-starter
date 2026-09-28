"""Shared test scaffolding. Complete — you shouldn't need to change this
for the exercises in this checkpoint, though you're welcome to add more
fixtures here as later exercises need them."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from reqtriage.config import Settings
from reqtriage.models import TriageRequest

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURES_DIR = REPO_ROOT / "tests" / "fixtures" / "llm_responses"


@pytest.fixture()
def settings() -> Settings:
    return Settings.load(repo_root=REPO_ROOT)


@pytest.fixture()
def make_request():
    def _make(**overrides):
        defaults = dict(
            request_id="req_test",
            source="ticket_form",
            description="Something is broken and needs triage.",
        )
        defaults.update(overrides)
        return TriageRequest.model_validate(defaults)

    return _make


def load_sample(request_id: str) -> TriageRequest:
    path = REPO_ROOT / "data" / "samples" / f"{request_id}.json"
    raw = json.loads(path.read_text(encoding="utf-8"))
    return TriageRequest.model_validate(raw)


def fixture_path(name: str) -> Path:
    return FIXTURES_DIR / f"{name}.json"
