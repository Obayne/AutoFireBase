Title: docs(backend): add DATA_MODEL and schema_version with tests

Summary
- Documents backend DTOs and their JSON serialization format.
- Adds `backend/schema_version.py` with `CURRENT_VERSION` and compatibility helpers, plus tests.

Changes
- New: `docs/DATA_MODEL.md`
- New: `backend/schema_version.py`
- New: `tests/backend/test_schema_version.py`
- Task: `tasks/docs-data-model-and-schema-version.md`

Rationale
- Clarify data interchange and provide forward-compat policy for loaders/saves.
- Make version access/compatibility easy and test-covered.

Test Plan (agents pulling this)
- From repo root:
  - `python -m pip install -e .` (or set `PYTHONPATH` to repo root)
  - `ruff check backend/schema_version.py tests/backend/test_schema_version.py`
  - `black --check backend/schema_version.py tests/backend/test_schema_version.py`
  - `pytest -q tests/backend/test_schema_version.py`

Notes
- Compatibility policy: load accepts same major version; otherwise false.
- Keep docs and constant in sync when bumping.

Refs
- Issue: N/A (please update if applicable)

