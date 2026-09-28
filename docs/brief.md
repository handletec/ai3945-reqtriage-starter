# Agent brief — reqtriage (Engineering Request Triage)

TEMPLATE. This is the artefact Module 3 teaches you to write for this
agent, and Module 5 teaches you to keep versioned as the agent changes.
Fill in each section as you build the corresponding piece — don't try
to write the whole thing up front, and don't leave a section as prose
about what you *plan* to do; write down what's actually true of the
code once it exists.

A brief is not documentation you write after the fact for someone else.
It's the thing you check new code against before you accept it: "does
this match what the brief says the agent may do?" If a coding
assistant's output does something the brief doesn't mention, that's a
signal to look closer — either the brief is out of date, or the
assistant added something you didn't ask for.

## Objective

*(Given by the course scenario — you can fill this in now.)*

Given one free-text validation/test observation, propose a triage
judgement — category, priority, likely component and owner — so a human
on-call validation engineer spends less time on routine reading-and-routing and
more time on judgement calls that actually need a person. The agent
recommends; it never acts.

## Inputs

*(Given — see `reqtriage/models.py::TriageRequest`.)*

One `TriageRequest` per run: `request_id`, `source`, `description`
(free text), optional `reported_by`, `submitted_at`, `tags`. Supplied as
a JSON file on disk (`data/samples/*.json`).

## Outputs

*(TODO — fill in once `TriageResult` has real fields. What does a
finished run actually produce? List every field and, in one line each,
what it means.)*

## Allowed actions

*(TODO — fill in as you add each capability. Keep this list exactly in
sync with the code: if the agent can call a tool, name it here with its
read-only/read-write status and what data it touches. If it's a later
exercise before you have any tool yet, this list can honestly be just
"read the request text; propose a result" for now.)*

## Blocked actions (the agent has no authority to do any of the following)

*(TODO — but some of these you can reason about now, before writing any
code, precisely because they're things the agent should NEVER be able
to do regardless of implementation. Start this list early. A few
prompts to get you thinking: Can it write to anything? Can it notify
anyone? Can it make the final call on something risky without a human
seeing it? Can it run forever?)*

## Success criteria

*(TODO — fill in as you add tests. For each criterion, name the test
that checks it. A success criterion with no test behind it is a hope,
not a criterion.)*

## Known limits

*(TODO — every real system has some. What does this one deliberately
not handle well, and why is that an acceptable trade-off for this
course rather than an oversight? "The model's judgement quality is
unverified" belongs here from the very first exercise that calls a real
model at all — see README.md once you get there.)*

## Human-review boundaries

*(TODO — once there's a `needs_human_review` flag: list every condition
that forces it to `true`, regardless of what the model proposed. This
section is often the difference between "the agent is a helpful
assistant" and "the agent is quietly making decisions nobody asked it
to make.")*

## Provider status

*(TODO — which LLM provider is actually wired up right now, and is
there a live network call anywhere in this repo? Keep this section
honest and current — it's the fastest way for someone auditing this
repo to check "is this actually running against a real model or not,
and does anyone need to worry about credentials.")*
