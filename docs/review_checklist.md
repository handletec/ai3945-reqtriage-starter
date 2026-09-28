# Reviewing LLM-generated Python — a checklist

Use this whenever you accept code from a development assistant (Claude or
otherwise) into this repository. The patterns below are the ones that
actually show up, not a generic "be careful" list. Each item says what
to look for and how to check it in under a minute.

## 1. Hallucinated APIs

**Look for:** a method or parameter name that "sounds right" for a
library you use, but doesn't exist in the version you have pinned.
**Check:** does it match `requirements.txt`'s pinned version (pydantic
`2.13.5`, pytest `9.1.1`)? Run it. An `AttributeError` or `TypeError` at
the call site is this pattern; don't assume it's your typo.

## 2. Wrong-version library syntax

**Look for (pydantic specifically):** `.dict()` instead of
`.model_dump()`, `.parse_obj()` instead of `.model_validate()`,
`class Config:` instead of `model_config = ConfigDict(...)`, `@validator`
instead of `@field_validator`. These are pydantic v1 idioms that
assistants still generate constantly because so much v1 code is in
their training data.
**Check:** grep the diff for `.dict(`, `.parse_obj(`, `class Config`,
`@validator` — none of these should appear anywhere in `reqtriage/`.

## 3. Over-broad exception handling

**Look for:** `except Exception:` (or worse, bare `except:`) with no
comment saying which specific failure is expected and why swallowing it
is safe.
**Check:** every `except` you accept should name a specific exception
and either re-raise, convert to a typed result, or log — never silently
`pass`.

## 4. Silent defaults that hide a real problem

**Look for:** `.get("field", "")` or `getattr(x, "y", None)` used to
avoid a `KeyError`/`AttributeError` in a place where a missing value
actually means something is wrong upstream.
**Check:** would a missing value here be a legitimate "no data" case, or
is it papering over a bug that should be visible? If in doubt, let it
raise in development and convert to a typed failure deliberately.

## 5. Unnecessary abstractions

**Look for:** a new base class, a plugin registry, a factory function,
or a config object introduced for something that has exactly one
implementation and no stated plan for a second. Assistants tend to
generalise prematurely because "flexible" code pattern-matches as
"good" code in their training data.
**Check:** is there a stated plan for a second implementation anywhere
in `docs/brief.md` or this repo's docs? If not, could you delete the
abstraction and inline the one thing it does? If yes, do that. (You'll
see this exact pattern named later in the course, once there's a real
second implementation to compare against — it's worth having the
instinct now, before that point.)

## 6. Changed interfaces

**Look for:** a generated edit that quietly changes a function's
signature, return type, or a model's field names/types while "fixing"
something else nearby.
**Check:** re-run `pytest` after every accepted suggestion, not just at
the end of a session. A changed signature that breaks a caller shows up
immediately; a changed signature that *doesn't* break any caller because
nothing calls it yet is exactly the kind of drift that isn't caught
until later — check the diff, not just the test result.

## 7. Invented requirements / scope creep

**Look for:** a generated tool, field, or code path that does something
the brief (`docs/brief.md`) never asked for — "while I was at it, I also
added a `notify_owner()` helper" is the textbook example, and it is
exactly the kind of thing this course's brief explicitly forbids.
**Check:** does every new capability trace back to a line in
`docs/brief.md`'s "Allowed actions"? If not, it doesn't go in, no matter
how reasonable it looks in isolation.

## 8. Tests that mirror the implementation instead of the behaviour

**Look for:** a generated test that asserts the exact internal steps a
function takes ("calls `json.loads` once, then `model_validate` once")
rather than its observable behaviour, or a test that asserts exact
prose output from a model instead of a structural invariant.
**Check:** would this test still pass after a legitimate internal
refactor that doesn't change behaviour? Would it still pass after a
harmless prompt wording change? Assert on fields and invariants, never
on exact free-text output a model produced.

## 9. Missing failure handling

**Look for:** a generated function that handles the success path
beautifully and has no story at all for "the file doesn't exist", "the
list is empty", or "the JSON doesn't parse".
**Check:** for anything touching model output, external data, or a
reference file, cross-reference `docs/brief.md`'s "Known limits" and
"Human-review boundaries" once those sections exist — every failure mode
listed there should map to a real, tested code path, not a comment
promising one.

## 10. Confident but wrong docstrings/comments

**Look for:** a generated docstring that describes what the function
*should* do rather than what the code actually does — often subtly
wrong after a follow-up edit changes the implementation but not the
comment above it.
**Check:** read the docstring last, after reading the code, and ask
"does this still match?" This is a two-second check that catches a
surprising fraction of drift.

---

None of this is about distrusting the assistant in general — it is about
treating its output the way you would a capable but unfamiliar
contributor's first pull request: read it, run it, and check it against
the brief before it goes in.
