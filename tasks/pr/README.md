PR Checklist (copy-paste for agents)

- Scope
  - Keep PR ≤300 LOC and focused on one task.
  - UI-only changes stay under `frontend/`; algorithms under `cad_core/`; glue in `backend/`.

- Lint/Format
  - `ruff check cad_core backend frontend tests`
  - `black --check cad_core backend frontend tests`

- Tests
  - Add/adjust tests for logic changes.
  - Run targeted: `pytest -q tests/<area>/...`

- Branching
  - Use `feat/<name>`, `fix/<name>`, `chore/<name>`, or `docs/<name>`.
  - Reference issue number in PR description if applicable.

- Notes
  - Avoid implicit import side-effects; minimize module-level state.
  - Document data model changes in `docs/DATA_MODEL.md` when relevant.

