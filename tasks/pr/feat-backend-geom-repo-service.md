Title: feat(backend): add in-memory geometry repo and ops service stubs

Summary
- Introduces a minimal in-memory repo for primitives (points, segments, circles) and an ops service shell.
- Enables orchestrating CAD core operations via a backend boundary (to be extended in follow-ups).

Changes
- New: `backend/geom_repo.py` (CRUD with deterministic IDs)
- New: `backend/ops_service.py` (create segment, placeholder op wiring)
- New: `backend/models.py` (DTOs used by repo/service)
- Task: `tasks/feat-backend-geom-repo-service.md`

Rationale
- Establish a clean separation between CAD algorithms and data persistence.
- Provide testable, non-global composition for future operations.

Test Plan (agents pulling this)
- From repo root:
  - `python -m pip install -e .` (or set `PYTHONPATH` to repo root)
  - `ruff check backend/geom_repo.py backend/ops_service.py backend/models.py`
  - `black --check backend/geom_repo.py backend/ops_service.py backend/models.py`
  - Quick import smoke: `python -c "import backend.geom_repo, backend.ops_service; print('ok')"`

Notes
- No external side effects; state is in-memory per instance.
- Follow-ups will add repo CRUD tests and first real op (trim/extend).

Refs
- Issue: N/A (please update if applicable)

