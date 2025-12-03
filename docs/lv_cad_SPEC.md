# lv_cad — Specification

## Overview

`lv_cad` is a standalone, pure‑Python CAD geometry and algorithms package extracted from this repo’s legacy `cad_core`. It provides deterministic, well‑tested primitives and operations (e.g., fillet, offset) without any UI or side‑effectful imports. The goal is a clean, reusable core that the desktop app (`app`/`frontend`) and headless tools can depend on.

## Goals

- Stable, documented public API for geometry primitives and CAD operations
- Parity with legacy `cad_core` behavior validated via tests and fixtures
- Minimal dependencies; optional extras for heavy libs (e.g., shapely, numpy)
- Zero UI/Qt imports and no network or file I/O at import time

## Non‑Goals

- Rendering, UI wiring, or DXF/UI tool dialogs (handled by `app`/`frontend`)
- Major algorithm rewrites beyond parity/correctness (optimizations later)

## Runtime and Platforms

- Python 3.11+
- Cross‑platform (Windows/macOS/Linux)
- Optional extras: `lv_cad[shapely]`, `lv_cad[numpy]`

## Package Layout (initial)

```text
lv_cad/
  __init__.py               # re‑exports: Point, Vector, fillet, etc.
  py.typed                  # type hints are part of the package
  geometry/
    __init__.py
    point.py                # Point, Vector dataclasses
    # (future) line.py, arc.py, polyline.py, bbox.py
  operations/
    __init__.py
    fillet.py               # parity-first wrappers; legacy fallback
    # (future) offset.py, transform.py, boolean.py
  util/
    __init__.py
    exceptions.py           # InvalidGeometryError, TopologyError, NumericPrecisionError
  tests/
    conftest.py             # path shim
    test_fillet_parity.py   # parity test for fillet
```

## Public API (early surface)

- `geometry.point`
  - `Point(x: float, y: float)`
    - methods: `to_dict() -> dict[str, float|str]`, `from_dict(d: dict[str, float|int|str]) -> Point`, `translate(dx, dy) -> Point`
  - `Vector(dx: float, dy: float)`
    - methods: `to_tuple() -> tuple[float, float]`
- `operations.fillet`
  - `fillet_line_line(...)` — parity wrapper delegating to `cad_core` for now
  - `fillet(...)` — convenience wrapper routing to line‑line variant initially
- `util.exceptions`
  - `InvalidGeometryError`, `TopologyError`, `NumericPrecisionError`

Design rules:

- Return new objects; do not mutate inputs (unless clearly documented)
- Keep function signatures simple; avoid hidden globals/state
- Document numeric tolerance expectations where relevant

## Data Shapes & Serialization

- Use simple `@dataclass` types for primitives
- JSON‑friendly `.to_dict()`/`.from_dict()` for fixtures and parity testing
- Example Point JSON: `{ "type":"Point", "x":1.0, "y":2.0 }`

## Error Modes & Tolerance

- Typed exceptions for invalid geometry, topological impossibility, or numeric issues
- Define standard numeric tolerances (later in `util.numeric.py`), allow per‑call overrides
- Edge cases to handle and document:
  - Zero‑length segments
  - Nearly collinear points
  - Fillet radius too large for given geometry

## Testing Strategy

- Parity‑first: each extracted algorithm has a parity test comparing legacy `cad_core` vs `lv_cad` outputs with agreed tolerance
- Unit tests for happy paths and edge cases
- Tests run headless; no UI imports
- CI gates for `ruff`/`black` and test runs on each PR

Acceptance for merging a migrated module:

- All parity and unit tests pass locally and on CI
- No UI imports introduced into `lv_cad`
- API docstrings reflect intended usage and constraints

## Packaging & Distribution

- Installable from repo root (`pip install -e .`)
- `py.typed` shipped for consumers using static typing
- Optional extras declared for heavy dependencies

## Migration (Strangler Pattern)

1. Scaffold `lv_cad` (done) with parity harness
2. Extract one algorithm at a time (fillet first — done as legacy wrapper)
3. Implement native `lv_cad` algorithm; keep legacy fallback until parity verified
4. Update callers via thin shims or direct imports once parity is green
5. Remove legacy code in small PRs after stable adoption

Rules:

- One feature/algorithm per PR; keep diffs small
- No `app/main.py` refactors in the same PR as algorithm moves
- Avoid module‑level side effects; prefer factories and explicit setup

## CI & Release

- Required checks: `ruff`, `black`, tests on all supported OSes (Windows job prioritized for PySide6 elsewhere)
- Tag releases when `lv_cad` reaches stable milestones; integrate wheel into PyInstaller builds as needed (outside this package)

## Next Steps (immediate)

- Add `offset.py` wrapper + parity test
- Implement native `fillet` (replace legacy delegate) with the same test harness
- Add `geometry.line/arc/polyline` minimal primitives to support more ops
- Wire import shim in legacy `cad_core` to prefer `lv_cad` where present

## Success Criteria for Phase 1

- `lv_cad` importable and tests pass locally and in CI
- Fillet and one additional operation (offset) are parity‑green
- No UI/Qt imports anywhere in `lv_cad`
- Short README and this spec kept up‑to‑date

---

## Agent Review Log

### Entry 2025-11-12T23:40:00Z — GitHub Copilot (Model: GPT-5)

**Summary:** Initial migration strategy is solid: clear separation, strangler pattern, parity-first discipline, small PR rule, typed core. Enhancements recommended for quantitative rigor and rollback safety.

**Strengths:** Clear scope boundaries; incremental algorithm extraction; explicit acceptance criteria; isolation from UI; dataclass + typed package; small diffs policy.

**Gaps Identified:** Missing numeric tolerance definitions; no performance baseline or regression threshold; lack of deprecation / rollback policy; parity lacks quantitative error bounds; test coverage targets absent; migration ordering beyond first steps not prioritized; no rollback env flag; removal criteria for legacy code not time‑bound.

**Recommendations:**

1. Add `util.numeric.py` with `ABS_EPS=1e-9`, `REL_EPS=1e-7`, helper `assert_close(a,b,abs=ABS_EPS,rel=REL_EPS)`.
2. Define parity pass criteria: max abs diff ≤1e-6, rel diff ≤1e-6 across sampled outputs.
3. Introduce performance smoke tests (optional gated by `RUN_PERF=1`) comparing native vs legacy ops; fail if regression >2% for typical sizes.
4. Add migration ordering table (line → arc → polyline → offset → fillet native → boolean → transform).
5. Introduce env flag `LV_CAD_FORCE_LEGACY=1` to revert delegation for any operation while native code stabilizes.
6. Deprecation timeline: legacy path marked deprecated after 2 green releases + 14 days with no regressions; remove ≥30 days post deprecation.
7. Specify coverage targets: geometry primitives ≥95% function, operations ≥90% branch.
8. Add rollback checklist (restore legacy import, disable native path via env, re-run parity + perf tests).
9. Track metrics (CSV or JSON) for each migrated op: abs/rel deltas, ms timings, memory snapshot.
10. Expand "Success Criteria" to include numeric + perf + coverage thresholds.

**Next Proposed Patch (Phase 1 Enhancements):** Append sections: Numeric Tolerances, Performance Baseline, Migration Ordering, Deprecation & Rollback, Coverage Targets. (Pending approval.)

---

## Numeric Tolerances

- Defaults: `ABS_EPS = 1e-9`, `REL_EPS = 1e-7` (in `lv_cad.util.numeric`).
- Helper: `assert_close(a, b, abs_tol=ABS_EPS, rel_tol=REL_EPS)` for tests and parity checks.
- All operations must document which comparisons are absolute vs relative and any per-call overrides.

## Performance Baseline

- Perf smoke tests (opt-in via env `RUN_PERF=1`) compare native `lv_cad` vs legacy for representative inputs.
- Thresholds: regression budget ≤2% runtime for small/medium inputs (increase budget temporarily if correctness work precedes optimization).
- Track simple CSV per op: samples, avg_ms_native, avg_ms_legacy, delta%.

## Migration Ordering

1. Primitives: line, arc, polyline, bbox
2. Ops: offset (wrapper → native), fillet (wrapper → native)
3. Ops: transform, boolean, measure
4. Shims: prefer `lv_cad` via adapters; remove legacy in small PRs once green

## Deprecation & Rollback

- Env flag `LV_CAD_FORCE_LEGACY=1` forces delegation to legacy for any guarded op.
- Deprecate legacy path after 2 green releases + 14 days without regressions; remove ≥30 days after deprecation.
- Rollback checklist: re-enable legacy flag; restore adapter import; re-run parity + perf; file incident note.

## Coverage Targets

- Geometry primitives: ≥95% function coverage
- Operations: ≥90% branch coverage
- Parity tests: cover happy-path and edge cases (zero-length, near-collinear, extreme radii)
