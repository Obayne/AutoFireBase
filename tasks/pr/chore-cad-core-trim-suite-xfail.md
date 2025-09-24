Title: test(cad_core): add xfail scaffolds for trim/extend arc-line operations

Summary
- Adds placeholder xfail tests to guide implementation of arc-line trim/extend operations without breaking CI.

Changes
- New: `tests/cad_core/test_trim_suite_xfail.py` (3 xfail tests with rationale)

Rationale
- Provide concrete acceptance targets for upcoming geometry work.
- Keep main green via xfail markers until implemented.

Test Plan (agents pulling this)
- `ruff check tests/cad_core/test_trim_suite_xfail.py`
- `black --check tests/cad_core/test_trim_suite_xfail.py`
- `pytest -q tests/cad_core/test_trim_suite_xfail.py` (shows 3 xfailed)

Notes
- No runtime imports of unimplemented APIs; tests call `pytest.xfail` directly with reasons.

Refs
- Task: `tasks/feat-cad-core-trim-suite.md`