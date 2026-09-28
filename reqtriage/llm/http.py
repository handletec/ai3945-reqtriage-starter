"""Stub for a real, HTTP-backed LLM provider.

This file intentionally does NOT call any network endpoint. Intel has not
confirmed a runtime LLM/API for this course, so this reference build does
not invent one, does not send any data anywhere, and does not depend on
any credentials existing. `config/settings.toml` always ships with
`llm.provider = "fake"`; selecting `"http"` here raises a clear error
rather than silently doing nothing or guessing at an endpoint shape.

When a provider IS approved, complete this class:

1. Read `LLM_ENDPOINT` / `LLM_API_KEY` / `LLM_MODEL` via
   `reqtriage.config.get_secret()` (real environment variables — never
   `.env` auto-loading, never a value hard-coded here).
2. Implement `complete()` using `urllib.request` (stdlib; no new
   dependency) with the approved endpoint's request/response shape,
   `settings.llm.timeout_seconds` as the timeout, and one retry on a
   transient network error.
3. Populate `LLMResponse.model_id` from the endpoint's response if it
   reports one, otherwise fall back to `settings.llm.model_id`.
4. Never log the API key. Never log the full request/response body by
   default — see logging_setup.py's guidance on what not to log.

Everything above this class (`agent.py`, `validation.py`, `rules.py`) is
already provider-independent: completing this one file is the entire
migration.
"""

from __future__ import annotations

from reqtriage.llm.base import LLMResponse


class HttpLLMNotConfiguredError(Exception):
    """Raised whenever something tries to use the HTTP provider before it
    has been completed for an approved endpoint."""


class HttpLLM:
    """Placeholder implementation of `LLMClient`. Not usable until the
    steps in this module's docstring are done."""

    def __init__(self, *_args: object, **_kwargs: object) -> None:
        raise HttpLLMNotConfiguredError(
            "llm.provider = 'http' is selected in settings.toml, but "
            "reqtriage/llm/http.py has not been implemented yet — there is "
            "no approved runtime LLM endpoint for this course. Set "
            "llm.provider back to 'fake', or complete this file once Intel "
            "confirms an endpoint (see this file's module docstring)."
        )

    def complete(self, system: str, user: str) -> LLMResponse:  # pragma: no cover
        raise HttpLLMNotConfiguredError("HttpLLM.complete() is not implemented")
