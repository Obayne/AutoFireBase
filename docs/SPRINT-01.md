Sprint 01 Workplan — AutoFire

Goals
- Keep `main` green; all work via short-lived PRs.
- Establish a thin vertical slice: open a project, view/edit simple geometry, persist, and test.
- Ensure Black/Ruff/pre-commit and CI pass on every PR.

Branches (create as needed)
- feat/frontend-model-space
- feat/backend-settings-and-store
- feat/cad-core-geometry-basics
- fix/ci-lint-orchestrations (only if CI requires tweaks)

Definition of Done
- Branch follows naming rules and has ≤300 changed LOC per PR.
- Tests cover new logic; `tests/` updated accordingly.
- Black (L100) and Ruff pass; no unused imports.
- No implicit module side effects; clear boundaries (frontend/backend/cad_core).

Workstreams and Tasks

Frontend (Qt)
- Model Space view shell
  - Implement a minimal Model Space widget and route for opening a project.
  - Hide Sheets dock by default; add a toggle in View menu.
  - Add Space selector + lock UI (non-functional toggle wired to backend stub).
  - Command bar widget stub with signal emission on Enter.
  - Acceptance: launching the app shows Model Space; commands emit signals; no crashes.

- Input handling foundation
  - Centralize key/mouse events in a small handler class.
  - Acceptance: events logged via a signal; unit test for key mapping.

Backend
- Settings service
  - Define a typed settings object (e.g., pydantic/dataclass) with load/save to disk.
  - Acceptance: round-trip test ensures persistence and defaults.

- Catalog store (SQLite)
  - Wrap SQLite access for seed/types/devices/specs with simple CRUD.
  - Provide an interface consumed by frontend to list/search items.
  - Acceptance: fixture DB created in tests; CRUD covered with pytest.

cad_core
- Geometry primitives and units
  - Implement basic entities (Point, Vector, LineSegment) and unit helpers.
  - Pure functions for transform (translate/scale/rotate) with tests.
  - Acceptance: deterministic outputs; no UI dependencies; 100% covered by unit tests.

Tests
- Add small fixtures for temp project directory and in-memory SQLite.
- Add pytest markers for slow/db if needed; keep default run fast (<10s).

CI and Tooling
- Ensure `pyproject.toml` configures Black/Ruff; wire pre-commit (local) and validate in CI.
- Add `pytest -q` step in CI if not present; keep cache usage minimal.

Suggested PR Sequence (vertical slices)
1) cad_core: geometry primitives + tests.
2) backend: settings service + tests.
3) backend: catalog store + tests (SQLite fixtures).
4) frontend: model space shell + command bar stub wired to backend stubs.
5) frontend: input handling + simple command execution that logs.

Owner Handoff Notes
- Run `. .venv/Scripts/Activate.ps1` then `pip install -r requirements-dev.txt`.
- Pre-commit: `pre-commit install`; run `pre-commit run --all-files` before pushing.
- Test quickly: `pytest -q` (skip if not installed locally; rely on CI).

Open Questions
- Confirm UI framework pin (PySide6 vs PyQt6) and minimum versions.
- Confirm DB file location and schema migration approach (alembic vs hand-rolled).
- Confirm command architecture (text commands vs palette-style actions).
