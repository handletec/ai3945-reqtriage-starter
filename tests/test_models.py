"""Tests for `TriageRequest` — complete, since the model is complete.

Everything else in `reqtriage/models.py` is a stub (see that module's
docstring). Add tests for each one alongside the exercise that fills it
in — don't write assertions against fields that don't exist yet."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from reqtriage.models import TriageRequest


def test_minimal_valid_request():
    request = TriageRequest(request_id="req_x", source="ticket_form", description="Something broke.")
    assert request.request_id == "req_x"
    assert request.tags == []
    assert request.reported_by is None


def test_full_request_round_trips():
    request = TriageRequest.model_validate(
        {
            "request_id": "req_y",
            "source": "email",
            "description": "Access request for remote lab access.",
            "reported_by": "dana.okafor",
            "submitted_at": "2026-09-10T08:15:00Z",
            "tags": ["access", "remote-lab-access"],
        }
    )
    assert request.reported_by == "dana.okafor"
    assert request.tags == ["access", "remote-lab-access"]


def test_empty_request_id_is_rejected():
    with pytest.raises(ValidationError):
        TriageRequest(request_id="", source="ticket_form", description="x")


def test_missing_description_is_rejected():
    with pytest.raises(ValidationError):
        TriageRequest.model_validate({"request_id": "req_z", "source": "ticket_form"})


# TODO (later exercise): once TriageProposal has real fields, add a test
# file for it here (or below) that checks at minimum: a valid proposal
# round-trips, and a proposal missing a required field is rejected.
