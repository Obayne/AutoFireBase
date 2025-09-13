AutoFire — Features Backlog (Living)

This file captures in-flight ideas we agreed to track but not ship yet.

Layout Space (Paper) — Generic Workflow
- Generic palette: basic symbols (detector, strobe, horn/strobe, speaker, pull, text markers).
- Underlays: import PDF/DXF, scale, set viewport, place generic devices on Paper layers.
- Layers: per-generic-type layers (e.g., AF_PAPER_SMOKE, AF_PAPER_STROBE, …); app understands these.
- Post-processing: map Paper generics → real Model devices later (bulk multi‑select assign).
- Attributes: Paper items carry minimal attributes; Model mapping attaches catalog attributes.
- Wiring later: optional single‑line “routes” that can expand to multiple cables.

Model Space — Accuracy & Calculations
- Distances/tolerances: consistent units, numeric tolerances, robust snap/measure tools.
- Voltage drop: wire gauge affects drop; support multi‑cable runs; per‑segment length and load.
- Reports: device schedules; wire length per gauge/run; power calculations.

Device Placement UX
- Stabilize “place on click” (no accidental drops on move); optional ghost preview.
- Sticky layer for placement target; explicit toggle for Paper annotations vs Model devices.

Appearance & Layout
- Presets: Dark+Red (light fonts, thin red accents), Light, High Contrast.
- Accent color slider (done for border accents); consider full theme sliders later if low risk.
- Workspace minimalism: dock/float/hide menus and remember layout; Settings to control it.

Help & Commands
- Command Reference dialog (done) + docs page.
- Autocomplete (done) with fuzzy match toggle; add more aliases.

Notes
- Paper‑space placement should not affect Model DB; mapping step links to the catalog.
- Keep main stable: small PRs, tests for conversion/mapping logic when added.

