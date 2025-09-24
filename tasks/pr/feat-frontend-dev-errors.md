Title: feat(frontend): live error bus + env-gated Dev Errors dock

Summary
- Adds `frontend.dev_errors` providing a lightweight logging-backed error bus capturing errors and uncaught exceptions.
- When `FRONTEND_DEV_ERRORS` is set, frontend installs the bus and the app adds a Dev Errors dock (under Dev menu) that updates live.

Changes
- New: `frontend/dev_errors.py` (ErrorBus, logging handler, excepthook chaining).
- Update: `frontend/__init__.py` installs bus when env var set.
- Update: `app/main.py` adds Dev menu entries and a Dev Errors dock when env var set.
- Tests: `tests/frontend/test_dev_errors_bus.py` (verifies bus captures logging errors).

Test Plan
- `ruff check frontend/dev_errors.py tests/frontend/test_dev_errors_bus.py`
- `black --check frontend/dev_errors.py tests/frontend/test_dev_errors_bus.py`
- `pytest -q tests/frontend/test_dev_errors_bus.py`

Notes
- UI remains unchanged unless `FRONTEND_DEV_ERRORS=1`.
- Bus tolerates subscriber errors; does not alter global logging level.