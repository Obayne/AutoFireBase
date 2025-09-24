Task: Backend – Geometry repo and ops service

Scope
- Add `backend/geom_repo.py` for in-memory storage of primitives (points, segments, circles) with simple IDs.
- Add `backend/ops_service.py` exposing pure functions that orchestrate `cad_core` ops over repo entities.

Details
- CRUD on repo with deterministic ID generation for tests.
- Service methods: create/update primitives; trim/extend lines; compute intersections; returns DTOs.
- Keep no global state; compose via explicit repo instance injection.
- Tests in `tests/backend/` use only in-memory repo and DTO serializers.

Acceptance
- Round-trip tests for repo CRUD and at least one op (e.g., trim-to-intersection) pass.
- `ruff` and `black --check` pass.

Branch
- `feat/backend-geom-repo-service`

