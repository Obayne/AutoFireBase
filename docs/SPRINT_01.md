# Sprint 01 – Kickoff Plan

## Cad Core – Trim/Extend/Fillet Suite
- Branch: `feat/cad-core-trim-suite`
- Goal: Correct, predictable trim/extend/fillet on lines/arcs.
- Acceptance
  - Unit tests for typical and edge cases (collinear, no intersection, tangent).
  - Pure functions in `cad_core/` (no Qt imports).
  - Documented function signatures and behavior.

## Backend – .autofire Schema & Loader
- Branch: `feat/backend-schema-loader`
- Goal: Define versioned JSON schema for drawings; implement round-trip load/save.
- Acceptance
  - `backend` APIs: `save(project) -> str`, `load(str|path) -> project`.
  - Tests: save/load round-trip equality on minimal fixture.
  - Version field + forward-compat strategy documented.

## Frontend – Tool Wiring & Shortcuts
- Branch: `feat/frontend-tools-wiring`
- Goal: Cleanly register tools/shortcuts; decouple UI from algorithms.
- Acceptance
  - Single registry for tools with names, icons, shortcuts.
  - No geometry logic in UI methods; calls into `cad_core`.
  - Smoke test for startup remains passing.

## QA – Test Harness & Fixtures
- Branch: `feat/qa-harness-and-fixtures`
- Goal: Expand pytest harness; tiny fixtures for geometry and I/O.
- Acceptance
  - `tests/` structure for cad_core ops and backend I/O.
  - Add 8–12 unit tests; CI green.

## Integration – Split app/main.py (Phase 1)
- Branch: `feat/integration-split-main`
- Goal: Extract boot/wiring from `app/main.py` into `frontend/` without behavior change.
- Acceptance
  - New `frontend/app.py` (or similar) hosts Qt app/boot.
  - Legacy code imports adjusted minimally; app still runs.
  - No geometry logic moved into UI; keep seams.
