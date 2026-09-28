"""Configuration for reqtriage.

This module is complete scaffolding — you shouldn't need to change it
for the exercises in this checkpoint. It hardcodes a few Python
constants (no settings file yet) and gives you the paths you'll need:
`data.samples_dir` for the sample requests, `data.owners_path` for the
component-owner reference data, and `fake_llm.fixtures_dir` for where a
`FakeLLM` fixture file should live once you build one.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class ConfigError(Exception):
    """Raised for a malformed or unsupported configuration."""


@dataclass(frozen=True)
class LLMSettings:
    provider: str
    model_id: str


@dataclass(frozen=True)
class DataSettings:
    samples_dir: Path
    owners_path: Path


@dataclass(frozen=True)
class FakeLLMSettings:
    fixtures_dir: Path


@dataclass(frozen=True)
class Settings:
    repo_root: Path
    llm: LLMSettings
    data: DataSettings
    fake_llm: FakeLLMSettings

    @staticmethod
    def load(repo_root: Path | None = None) -> "Settings":
        root = repo_root or REPO_ROOT
        return Settings(
            repo_root=root,
            llm=LLMSettings(provider="fake", model_id="fake-llm-v1"),
            data=DataSettings(
                samples_dir=(root / "data" / "samples").resolve(),
                owners_path=(root / "data" / "reference" / "component_owners.csv").resolve(),
            ),
            fake_llm=FakeLLMSettings(
                fixtures_dir=(root / "tests" / "fixtures" / "llm_responses").resolve(),
            ),
        )


def get_secret(name: str) -> str | None:
    """Read a secret from a real environment variable. Never reads `.env`
    or any file — the process environment is the only source. Not used
    by anything yet (there is no live provider); provided now so its
    contract doesn't change later."""

    return os.environ.get(name)
