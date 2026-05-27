# Live FieldWorks Testing Workflow

This suite ships a parallel "live-DB" testing track that exercises the
operations classes against a real `.fwdata` project on the developer's
machine (the standard candidates are `Sena 3`, `Test`, `SampleLexicon`,
`SampleLexicon3`). Live tests need FieldWorks installed and the project
reachable on disk -- they are skipped automatically in CI / mock-only
environments.

## Running the live suite

To run only the live tests:

    pytest -m requires_live_project

To run everything EXCEPT live tests (mock-only fast suite):

    pytest -m "not requires_live_project"

The unfiltered `pytest` invocation still collects both buckets, so the
existing CI behaviour is preserved.

## Fail-loud on mock fallback

The session fixture in `tests/conftest.py` silently falls back to mock
mode when FieldWorks initialization fails (e.g. on a CI runner with no
FW install). When you intentionally want a live run and would rather see
a hard error than a quiet mock pass, set the environment variable:

    $env:FLEXLIBS_REQUIRE_LIVE = "1"
    pytest -m requires_live_project

This raises `pytest.UsageError` instead of degrading to mocks.

## Ledger and Markdown summary

After each run that actually executes one or more live tests,
`tests/conftest.py` writes `tests/live_status.json` -- a per-test and
per-class summary of pass / fail / skip outcomes. Pure mock runs do NOT
touch the file, so a CI run never overwrites a developer's live ledger.

Render the JSON as a human-readable Markdown table with:

    python scripts/render_live_status.py

The renderer also produces a "no data yet" stub if the JSON is missing
or empty, so the Markdown file is always present and well-formed.

## The two-marker pattern

There are two distinct markers:

* `requires_live_project` -- the **selector**. Every test that opens a
  real project is tagged with this so `pytest -m requires_live_project`
  / `pytest -m "not requires_live_project"` work as expected.

* `live_phase(operations_class, phase)` -- the **ledger metadata**.
  Records which Operations class and CRUD phase the test exercises.
  Valid phases: `read`, `add`, `reorder`, `modify`, `delete`. The
  session-finish hook aggregates per-(class, phase) status from these
  markers.

`live_phase` markers are populated incrementally. Existing tests do
**not** carry `live_phase` yet -- they appear under
"Uncategorized live tests" in `LIVE_STATUS.md` until they are
backfilled. This is expected for Cycle 1 of the rollout.
