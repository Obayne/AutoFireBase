# Team and Roles for GUI + Backend Fixes

This document outlines suggested roles, priorities, and tasks to get device placement and paperspace working reliably.

Roles
- Frontend Lead: fix palette, placement UX, ghost device, paperspace integration, and run GUI smoke tests.
- Backend Lead: audit `db/loader.py` and `catalog` APIs, add compatibility shims if schema changed, and provide deterministic fixtures for QA.
- QA/DevOps: run smoke tests, capture logs, and validate cross-platform behaviors; manage PRs and CI.
- Documentation: update `docs/UserGuide.md` and `docs/PaperSpace.md` with placement and paperspace workflows.

Initial tasks
1. Reproduce: developer reproduces placement failure and captures stdout/stderr logs.
2. Trace: identify call chain for palette selection -> view.set_current_device -> CanvasView mouse event -> DeviceItem creation.
3. Shim: if DB schema drift is detected, add compatibility mapping in `app/catalog.py` to normalize protos.
4. UI polish: show part_number/symbol when name missing, ensure active layer respected on placement, and ensure ghost coverage toggles are intuitive.
5. Paperspace: ensure viewport creation and paperspace group parenting work and can be saved/loaded.
6. Lint/Tidy: continue ruff/black pass and resolve E501 lines that block pre-commit.

Work flow
- Small PRs (<200 lines) per area, each with a short test (unit or smoke) and a descriptive PR body.

Contact
- Assign tasks in the PR description and tag the appropriate lead.
