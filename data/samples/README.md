# Sample requests

`example_001.json` and `example_002.json` are placeholders, not real
data — replace them with sample requests from your own capstone task
family. Keep the same shape (`reqtriage/models.py::TriageRequest`):
`request_id`, `source`, `description`, and the optional fields.

Aim for a small set (5–15 is plenty) covering: a normal case your agent
should handle cleanly, at least one case that should trigger your tool,
at least one case with missing or ambiguous information, and at least
one negative/edge case (something that should degrade safely or force
`needs_human_review`). The mandatory scope for the capstone is one tool,
one positive case, and one negative case — more is fine, less isn't.
