# Architecture Overview

Goal: decouple GUI from algorithms and persistence.

Packages
- `frontend/` (Qt/PySide6): windows, scenes, tools wiring, input events.
- `cad_core/` (pure Python): geometry ops, snapping, trim/extend/fillet, unit conversion.
- `backend/` (headless): data models, file I/O, `db/loader.py`, configuration, services.

Current State
- Legacy modules still live under `app/`, `core/`, and `db/`.
- We will incrementally migrate modules into the target packages while preserving behavior.

Migration Plan (phased)
1. Extract units/geometry helpers from `app/` into `cad_core/`.
2. Move `db/loader.py` and config into `backend/`.
3. Split `app/main.py` into `frontend/app.py` (Qt boot) and per-feature views.
4. Introduce service layer boundaries between frontend and cad_core/backend.

Testing
- Keep `cad_core/` pure and covered by unit tests.
- Avoid GUI in tests; mock Qt where needed.

