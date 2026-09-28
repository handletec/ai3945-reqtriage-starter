"""Configuration loading.

Everything non-secret lives in `config/settings.toml` and is loaded here
with the standard-library `tomllib` (Python 3.11+, no dependency). Every
path in the TOML file is relative to the repository root; this module
resolves them to absolute `Path` objects once, here, so nothing else in
the codebase has to guess where the repo root is.

Secrets are a separate concern. This module does NOT read a `.env` file
and does NOT depend on `python-dotenv`. If a real LLM endpoint is ever
approved, its credentials must be exported as real environment variables
before running the process (`export LLM_API_KEY=...` / the OS equivalent)
and read with `get_secret()` below. `.env.example` documents the expected
variable names for a human to set up; it is not loaded automatically by
anything in this package.
"""

from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class ConfigError(Exception):
    """Raised for a malformed or unsupported configuration — a class of
    failure a participant should see clearly, not as a stack trace deep
    inside agent.py."""


@dataclass(frozen=True)
class LLMSettings:
    provider: str
    model_id: str
    timeout_seconds: float


@dataclass(frozen=True)
class AgentSettings:
    # The autonomy dial (see reqtriage/agent.py): the number of
    # `call_tool` action opportunities available in one run. A request
    # spends one opportunity once it passes the budget check and enters
    # dispatch, even if dispatch reports unknown_tool, invalid_arguments,
    # or a tool error. L1 = 0, L2 = 1, L3 = a small number > 1.
    # This is NOT the number of times the model gets to speak — see
    # max_model_turns for that.
    max_tool_actions: int
    # A separate, independent hard safety bound on total model turns:
    # EVERY real `llm.complete()` invocation this run makes counts as
    # one turn (tool-call attempts, the final turn, AND the one
    # validation-repair call, with no exceptions — see
    # reqtriage/agent.py::call_model). This is what stops a misbehaving
    # model from looping forever even once its tool-action budget is
    # exhausted (e.g. it keeps asking for another tool anyway, or keeps
    # naming a tool that doesn't exist). Must leave room for at least
    # one turn beyond max_tool_actions or a well-behaved model could
    # never reach "final" — enforced in Settings.load() below.
    max_model_turns: int


@dataclass(frozen=True)
class PromptSettings:
    version: str
    system_path: Path
    user_path: Path


@dataclass(frozen=True)
class DataSettings:
    samples_dir: Path
    # TODO: once you add your own tool, add a field here pointing at its
    # read-only reference data (the reqtriage reference build had
    # `owners_path` pointing at `data/reference/component_owners.csv`)
    # and a matching key under `[data]` in `config/settings.toml`.


@dataclass(frozen=True)
class FakeLLMSettings:
    scenario_map_path: Path
    fixtures_dir: Path
    default_scenario: str


@dataclass(frozen=True)
class LoggingSettings:
    log_path: Path
    console_level: str


@dataclass(frozen=True)
class PolicySettings:
    confidence_threshold: float
    allowed_sources: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class Settings:
    repo_root: Path
    llm: LLMSettings
    agent: AgentSettings
    prompts: PromptSettings
    data: DataSettings
    fake_llm: FakeLLMSettings
    logging: LoggingSettings
    policy: PolicySettings

    @staticmethod
    def load(config_path: Path | None = None, repo_root: Path | None = None) -> "Settings":
        root = repo_root or REPO_ROOT
        path = config_path or (root / "config" / "settings.toml")
        if not path.is_file():
            raise ConfigError(f"Settings file not found: {path}")

        try:
            with path.open("rb") as f:
                raw = tomllib.load(f)
        except tomllib.TOMLDecodeError as exc:
            raise ConfigError(f"Could not parse {path}: {exc}") from exc

        def section(name: str) -> dict:
            try:
                return raw[name]
            except KeyError as exc:
                raise ConfigError(f"Missing [{name}] section in {path}") from exc

        def resolve(rel: str) -> Path:
            return (root / rel).resolve()

        try:
            llm = section("llm")
            agent = section("agent")
            prompts = section("prompts")
            data = section("data")
            fake_llm = section("fake_llm")
            logging_ = section("logging")
            policy = section("policy")

            settings = Settings(
                repo_root=root,
                llm=LLMSettings(
                    provider=llm["provider"],
                    model_id=llm["model_id"],
                    timeout_seconds=float(llm["timeout_seconds"]),
                ),
                agent=AgentSettings(
                    max_tool_actions=int(agent["max_tool_actions"]),
                    max_model_turns=int(agent["max_model_turns"]),
                ),
                prompts=PromptSettings(
                    version=prompts["version"],
                    system_path=resolve(prompts["system_path"]),
                    user_path=resolve(prompts["user_path"]),
                ),
                data=DataSettings(
                    samples_dir=resolve(data["samples_dir"]),
                ),
                fake_llm=FakeLLMSettings(
                    scenario_map_path=resolve(fake_llm["scenario_map_path"]),
                    fixtures_dir=resolve(fake_llm["fixtures_dir"]),
                    default_scenario=fake_llm["default_scenario"],
                ),
                logging=LoggingSettings(
                    log_path=resolve(logging_["log_path"]),
                    console_level=logging_["console_level"],
                ),
                policy=PolicySettings(
                    confidence_threshold=float(policy["confidence_threshold"]),
                    allowed_sources=tuple(policy.get("allowed_sources", [])),
                ),
            )
        except KeyError as exc:
            raise ConfigError(f"Missing required key {exc} in {path}") from exc

        if settings.llm.provider not in {"fake", "http"}:
            raise ConfigError(
                f"Unknown llm.provider {settings.llm.provider!r} — expected 'fake' or 'http'"
            )
        if settings.agent.max_tool_actions < 0:
            raise ConfigError("agent.max_tool_actions must be >= 0 (0 means L1: no tool calls)")
        if settings.agent.max_model_turns < 1:
            raise ConfigError("agent.max_model_turns must be >= 1")
        if settings.agent.max_model_turns <= settings.agent.max_tool_actions:
            raise ConfigError(
                "agent.max_model_turns must be greater than agent.max_tool_actions — "
                "otherwise a well-behaved model could exhaust its tool-action budget "
                "and never get a turn left to return a final action"
            )

        return settings


def get_secret(name: str) -> str | None:
    """Read a secret from a real environment variable. Never reads `.env`
    or any file — the process environment is the only source. Returns
    `None` if unset; callers decide whether that is an error."""

    return os.environ.get(name)
