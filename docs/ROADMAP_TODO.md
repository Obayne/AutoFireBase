# AutoFire roadmap TODO (high-priority, space-aware)

This plan prioritizes production-value features that differentiate vs AlarmCAD/FireCAD while protecting current working flows. Each item includes scope, acceptance criteria, and risk notes.

## P0 — Production deliverables (reports, compliance, addressing)

1) Reports & Outputs v1 (riser + schedules)
- Scope: Auto-generate riser diagram and cable schedule from live circuits.
- Accept: Riser image/PDF exports; cable schedule CSV (circuit, wire type, length, AWG, devices). BOM totals by device and wire SKU.
- Notes: Read-only first; editing in-place is P1.

2) Auto-addressing (SLC loops)
- Scope: Assign addresses per loop following policies (reserved ranges, no duplicates), lock before export.
- Accept: One-click “Assign Addresses”, warnings for conflicts, lock/unlock, export map.
- Notes: Deterministic ordering (panel→loop→path order) for reproducibility.

3) Compliance engine v1 (NFPA rules subset)
- Scope: Rule set for voltage drop threshold, loop length/device count, strobe candela groupings, basic spacing.
- Accept: Pass/Warn/Fail panel with jump-to issue; exportable compliance report.
- Notes: Start with what’s already computed (VD, counts), add 2–3 device spacing checks.

## P1 — Golden-path onboarding

4) New Project wizard + floorplan import (DXF/PDF)
- Scope: Wizard (client/address/AHJ), import floorplan, calibrate scale, lock arch layers.
- Accept: New project JSON manifest; successful import and calibrated snap; layers locked.
- Notes: Use ezdxf if available; PDF import via raster fallback acceptable initially.

5) Submittal packet assembly
- Scope: Package riser, schedules, BOM, datasheets, sequence of operations into a single export folder/zip.
- Accept: One-click export folder with timestamp; minimal templating.
- Notes: Keep simple; users can post-process.

## P2 — UX polish and competitive shine

6) Live calculations panel polish
- Scope: Side panel showing VD/battery/loop limits with color states; debounce recompute.
- Accept: Stable updates under heavy placements; no UI jank.

7) Placement assistant (gentle AI hints)
- Scope: Coverage halos + simple nudge text (e.g., “coverage gap 25 ft east”).
- Accept: Non-blocking hints; disable toggle; no auto-move.

8) Wire routing QoL
- Scope: Ortho/45° modes, corner drag, segment snap, quick split/merge.
- Accept: Keyboard shortcuts, predictable grips; preserves connectivity.

## Engineering tasks (safe, space-aware)

9) Workspace cleanup tooling (WhatIf by default)
- Scope: Script to prune build/, dist/, __pycache__/, .pytest_cache/, .ruff_cache/, old logs; keep last N artifacts.
- Accept: Dry-run shows reclaim size; deletes only with -Force; never touches source.

10) Headless smoke test in CI
- Scope: Ensure app imports and minimal controller init; optional GUI check with PySide6 if available.
- Accept: Green in PRs; catches startup regressions.

## Differentiators vs AlarmCAD/FireCAD (why we’ll win)
- Live code compliance vs static block placement.
- Multi-vendor, modern GUI; not tied to legacy CAD host.
- Real-time calculations; instant riser/schedules from actual circuits.
- Gentle AI hints for efficiency (not black-box auto-design).

## Suggested sequencing (8–10 days, focused)
- Day 1–2: Auto-addressing v1 + tests.
- Day 3–4: Riser + cable schedule exports.
- Day 5: Compliance v1 (counts/VD rules) + panel.
- Day 6: New Project wizard (skeleton) + DXF happy-path.
- Day 7: Submittal packet assembly.
- Day 8: Cleanup tooling + CI smoke test.

---
Owner: HAL + human maintainer. Keep PRs ≤300 lines; add/adjust tests.
