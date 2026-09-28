# Prompt changelog

Prompts are versioned artefacts, not inline strings. `config/settings.toml`
`[prompts] version` is the single source of truth for which version is
active, and every `RunMeta.prompt_version` in `logs/runs.jsonl` records
which version produced that run.

## Versioning convention

Whenever you change either prompt file (`prompts/triage_system.md` or
`prompts/triage_user.md`) in a way that changes model behaviour:

1. Bump the version comment at the top of the prompt file(s) you changed.
2. Bump `[prompts] version` in `config/settings.toml` to the SAME value,
   in the same change.
3. Add an entry below describing what changed and why.

Keeping both in sync matters because `RunMeta.prompt_version` is read
straight from `config/settings.toml` — if the prompt file and the config
value disagree, every run this checkpoint produces is mislabelled and a
later regression is much harder to trace back to the change that caused
it.

## v1-template — 2026-09-14 (current)

- Starting point for the capstone. Establishes the generic two-action
  vocabulary (`call_tool` / `final`) and the "you only propose, a program
  decides" framing — keep these.
- Everything else is a placeholder: the opening paragraph, the tool
  name/description, and every field inside `final.result` beyond the five
  generic ones (`summary`, `missing_info`, `confidence`,
  `needs_human_review`, `rationale`) are marked `[TODO: ...]` in
  `prompts/triage_system.md`.
- You are expected to rewrite this prompt once you add your own tool and
  domain fields to `TriageProposal`/`TriageResult`
  (`reqtriage/models.py`) — bump the version here and in
  `config/settings.toml` when you do, following the convention above.
