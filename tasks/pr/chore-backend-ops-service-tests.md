Title: test(backend): add CRUD-like test for OpsService create_segment

Summary
- Adds a targeted test for `OpsService.create_segment` to ensure the created segment is persisted via `InMemoryGeomRepo` and returns a proper `EntityRef`.

Changes
- New: `tests/backend/test_ops_service.py`

Rationale
- Provide a basic contract check for the ops service wiring before adding more operations (trim/extend).

Test Plan (agents pulling this)
- From repo root:
  - `python -m pip install -e .` (or set `PYTHONPATH` to repo root)
  - `ruff check tests/backend/test_ops_service.py`
  - `black --check tests/backend/test_ops_service.py`
  - `pytest -q tests/backend/test_ops_service.py`

Notes
- No external side effects; uses in-memory repo.

Refs
- Issue: N/A (update if applicable)