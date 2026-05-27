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

## Sena 3 fixture and restoration

The canonical live-test project is **Sena 3**. The golden fixture is
checked into `tests/fixtures/Sena 3 *.fwbackup` (gitignored, ~15 MB) and
is the source of truth between sessions. Phases B--D mutate the
in-place project; the restoration script wipes accumulated churn:

    # Restore Sena 3 from tests/fixtures/ into the FieldWorks projects dir
    python scripts/restore_sena3.py

    # Check current state without restoring
    python scripts/restore_sena3.py --check

    # Override target name / projects dir if needed
    python scripts/restore_sena3.py --target "Sena 3 Test" \
        --projects-dir "C:\Path\To\Projects"

Run this before every live session for a clean baseline. Re-run after
any session to discard test-induced timestamp / object churn.

## The five-phase stabilization model

Each operations class earns "stabilized" by passing every phase:

| Phase | Pattern | Risk | Where it runs |
|-------|---------|------|---------------|
| A. Read | `writeEnabled=False`, call getters | None | In-place on real Sena 3 |
| B. Add | Create with `TEST_` prefix, verify, delete in `finally:` | Low | In-place on real Sena 3 |
| C. Reorder | Capture order, swap, restore | Medium | In-place on real Sena 3 |
| D. Modify | Capture value, set new, assert, restore captured | Medium | In-place on real Sena 3 |
| E. Delete | Genuinely destructive | High | **Sandbox copy via `sena3_sandbox` fixture** |

The `sena3_sandbox` fixture (in `tests/conftest.py`) unzips the
`.fwbackup` into a `tempfile.mkdtemp()` directory, opens the resulting
`.fwdata` by absolute path, yields the project, and cleans the tempdir
on teardown. Use it for any test in Phase E.

Phases A--D accept LCM's auto-bump of `DateModified` on any write -- the
restoration script wipes that churn between sessions. Phase E never
touches the real project, so churn is irrelevant.

## Canonical template

The canonical end-to-end template is
`tests/operations/test_locations_live.py`. Replicate its structure
(one class per phase, `live_phase` markers, `TEST_` prefix, finally
cleanup, optional `sena3_sandbox` fixture) when adding live coverage
for new operations classes.
