Task: cad_core – Units tolerances tests

Scope
- Add focused tests for `cad_core/units.py`: `EPS`, `almost_equal`, `clamp`, `sgn`, `round_tol`.

Details
- New file: `tests/cad_core/test_units_tolerances.py` with small, isolated cases.
- Ensure no dependency on UI or other modules; pure functions only.
- Keep tolerance behavior consistent across core geometry.

Acceptance
- `pytest -q` passes; new tests cover edge cases (negative, swapped bounds, zero tol).
- `ruff` and `black --check` pass.

Branch
- `chore/cad-core-units-tolerances-tests`

