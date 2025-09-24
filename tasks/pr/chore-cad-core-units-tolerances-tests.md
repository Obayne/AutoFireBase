Title: chore(cad_core): add units tolerances tests

Summary
- Adds focused tests for `cad_core/units.py` covering `EPS`, `almost_equal`, `clamp`, `sgn`, and `round_tol`.
- Introduces `cad_core/units.py` helpers with improved `round_tol` using Decimal to avoid FP drift.

Changes
- New: `tests/cad_core/test_units_tolerances.py`
- New: `cad_core/units.py`
- Task: `tasks/chore-cad-core-units-tolerances-tests.md`

Rationale
- Establish consistent tolerance behavior used across core geometry.
- Provide small, pure tests to keep regressions visible and fast.

Test Plan (agents pulling this)
- From repo root:
  - `python -m pip install -e .` (or set `PYTHONPATH` to repo root)
  - `ruff check cad_core tests/cad_core/test_units_tolerances.py`
  - `black --check cad_core tests/cad_core/test_units_tolerances.py`
  - `pytest -q tests/cad_core/test_units_tolerances.py`

Notes
- No UI impact; pure functions only.
- Keep `EPS` and helpers as the single source of tolerance logic across CAD core.

Refs
- Issue: N/A (please update if applicable)

