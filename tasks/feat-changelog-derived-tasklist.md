# Tasklist: Feature Follow-ups From CHANGELOG

Goal: Turn CHANGELOG items into actionable follow-ups (impl gaps, tests, docs). Keep changes small and add tests with each PR.

## Coverage & Array
- [ ] Backend: Wire NFPA 72/manufacturer tables for strobe/smoke spacing and speaker dB models; provide strategy interface and pluggable data source. [area:backend]
- [x] Backend: Validate inverse-square speaker model against sample specs; add unit tests for dB targets at distances. [area:backend]
- [ ] Frontend: Ensure overlays only render for strobe/speaker/smoke device types (per v0.6.3); add tests for type filtering. [area:frontend]
- [ ] Frontend: Keyboard shortcuts ([ / ]) adjust strobe diameter ±5 ft; (Alt+[ / Alt+]) adjust speaker target dB ±1; add key handling tests. [area:frontend]
- [ ] Frontend: Live preview ghost + coverage follows cursor; add interaction test to assert preview toggles and updates size with adjustments. [area:frontend]
- [ ] Backend: Array placement uses coverage-driven spacing by default with manual override; add deterministic tests (seed) for grid generation. [area:backend]
- [ ] Persistence: Overlays and coverage settings persist in `.autofire` files; add round-trip tests. [area:backend]

## CAD Core Geometry & Modify Tools
- [ ] cad_core: Implement/verify algorithms for Offset, Trim, Extend, Rotate, Mirror, Scale, Chamfer; ensure numeric robustness and units. [area:cad_core]
- [ ] cad_core: Fillet/Corner and Fillet/Radius correctness at edge cases (tiny/large radii, parallel/colinear, tangency). Add property-based tests. [area:cad_core]
- [ ] cad_core: Arc-3pt and Circle tools numeric stability; tests for degenerate inputs and near-colinear picks. [area:cad_core]
- [ ] Backend: Expose geometry ops via `geom_repo`/`ops_service` with pure functions; add unit tests for each API. [area:backend]
- [ ] Frontend: Wire Draw/Modify tool actions to cad_core operations via tool_registry; add tool activation/smoke tests. [area:frontend]

## OSNAP & Grid
- [ ] Frontend: OSNAP toggles (Endpoint/Mid/Center/Inter/Perp) under View must persist in settings; add toggle+persist tests. [area:frontend]
- [ ] Frontend: Grid Style dialog (opacity, widths, major interval) persists to prefs and project; add tests for defaults and round-trip. [area:frontend]
- [ ] Frontend: Grid contrast is theme-aware (light/dark/high-contrast); visual config tests (values only). [area:frontend]

## Underlay (DXF/PDF) & Layers
- [ ] Backend: DXF import layer-aware rendering with visibility/color override/lock/print flags; add small DXF fixture and importer tests. [area:backend]
- [ ] Frontend: DXF Layers dock interactions (toggle visibility/lock/print) affect scene/export; add interaction tests. [area:frontend]
- [ ] Underlay scaling: reference line with real distance, factor, and drag modes; add geometry-consistency tests and UI smoke tests. [area:frontend]
- [ ] Export respects non-print layers; add export tests asserting layer masking in PNG/PDF outputs (metadata/scene graph level if headless). [area:frontend]
- [ ] Persist underlay transform with project; add save/load tests. [area:backend]

## Command Bar & Units
- [ ] Parser: Absolute (@x,y), Relative (dx,dy), Polar (r<θ) in feet/inches; add parsing/normalization tests. [area:backend]
- [ ] Frontend: Command Bar wiring to draw tools; add integration test for typed coordinates placing geometry at expected positions. [area:frontend]
- [ ] Units: Feet/inches conversions consistent across coverage, array, and geometry; add cross-module unit tests. [area:backend]

## Export/Print
- [ ] PNG/PDF export: letter landscape, fit-to-content; add headless render tests validating bounding boxes/margins. [area:frontend]
- [ ] Add smoke test generating a tiny project and verifying PDF/PNG files exist and are non-empty (CI-safe). [area:frontend]

## UI & Docks
- [ ] Device Palette dock tabbing with Properties and DXF Layers; add layout persistence tests. [area:frontend]
- [ ] Status bar shows Grid opacity/size; ensure live updates when grid style changes. [area:frontend]
- [ ] Improve panning (Space/Middle Mouse), Esc commits polyline; add interaction tests. [area:frontend]

## DB Catalog
- [ ] Create `%USERPROFILE%/AutoFire/catalog.db` on first run; seed demo devices when empty; add file-system fixture tests. [area:backend]
- [ ] Palette loads devices from DB if present; fallback to demo if missing; add loader tests. [area:backend]

## Annotations & Measure
- [ ] MText scalable annotation: verify font scaling and anchoring; add serialization tests. [area:frontend]
- [ ] Freehand sketch tool: basic smoothing and hit-testing; add round-trip tests. [area:frontend]
- [ ] Measure tool temporary readout correctness (units, precision); add tests. [area:frontend]

## Persistence
- [ ] Ensure overlays, grid style, device properties, and underlay state persist via `.autofire`; add comprehensive snapshot tests. [area:backend]

## Docs
- [ ] Update `docs/` with: Coverage model notes, Command Bar syntax, Underlay scaling guide, and DXF Layers usage. [area:docs]
- [ ] Add CHANGELOG entries when closing above tasks; keep Unreleased updated. [area:docs]

## QA & CI
- [ ] Add headless PySide6 test harness config and skip markers for GUI-unavailable envs. [area:qa]
- [ ] Add coverage gates for backend/cad_core; upload artifacts. [area:qa]

## Release Hygiene
- [ ] Verify v0.4.6/v0.4.7/v0.5.3/v0.6.2/v0.6.3 tags match CHANGELOG; add compare links. [area:chore]
- [ ] Fill CHANGELOG [Unreleased] with the next planned items (this tasklist references). [area:chore]

Notes
- Keep PRs scoped by area (frontend/backend/cad_core/docs) and include tests.
- Prefer small, incremental tasks. Use branches: `feat/<name>` or `fix/<name>` or `chore/<name>`.
