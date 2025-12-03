# LV CAD (Low Volt Layer Vision) – Agent Guide

Scope: Entire repository.

Principles

- Keep `main` green: all work via feature branches + PRs.
- Small, focused changes (≤300 lines) with clear rationale.
- Prefer composition over monoliths; avoid editing unrelated code.
- Focus on Layer Vision intelligence and precise CAD analysis.

Directory Layout (target state)

- `frontend/` – UI: Qt widgets, views, input handling.
- `backend/` – non-UI logic, persistence, loaders, settings.
- `cad_core/` – geometry kernels, tools, algorithms, units.
- `tests/` – pytest suite and tiny fixtures.
- `docs/` – architecture, decisions, and contribution guides.
- `build/` – build outputs (ignored). Packaging specs live at repo root for now.

Working Rules

- Code style: Black (line length 100) + Ruff; fix lint before commit.
- Tests: add/adjust tests with each change; no PR without tests if logic changed.
- Imports: do not rely on implicit side effects; keep module-level state minimal.
- UI vs core: GUI code stays in `frontend/`; algorithms in `cad_core/`; glue in `backend/`.

Branching

- `feat/<name>` for features, `fix/<name>` for fixes, `chore/<name>` for maintenance.
- Reference the GitHub issue number in the PR description.

Reviews

- HAL reviews and requests changes as needed. At least one human approval to merge.
