# Reference data

Empty on purpose — the reqtriage checkpoints' `component_owners.csv`
(and, at later checkpoints, `known_issues.json`) were data for tools
specific to that task. Your capstone tool needs its own read-only
reference data; put it here, in whatever format suits it (CSV, JSON,
whatever your tool's implementation reads), and point
`reqtriage/config.py`'s `DataSettings` at it the way `owners_path` used
to point at `component_owners.csv`.
