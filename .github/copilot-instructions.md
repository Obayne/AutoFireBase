<!-- Auto-generated guidance for AI coding agents working on LV CAD -->
# LV CAD — Copilot instructions

Keep guidance short and actionable. Focus on the concrete patterns and commands used by this repo.

- Big picture
  - Python desktop CAD-style app (PySide6 GUI) with core algorithms in `cad_core/`, UI in `frontend/` and `app/`, and non-UI glue in `backend/`.
  - `app/main.py` is the primary entrypoint for local development (`python app/main.py`). The project also uses PyInstaller specs (`LV_CAD.spec`, `LV_CAD_Debug.spec`) for builds.

- Developer workflows (copy-pasteable)
  - Dev setup (Windows PowerShell): `./setup_dev.ps1` — creates `.venv`, installs requirements, and sets up pre-commit.
  - Activate venv: `. .venv/Scripts/Activate.ps1`
  - Run app locally: `python app/main.py` (or `python -m frontend.app` in some branches)
  - Format/lint: `ruff check --fix .` then `black .` (pre-commit will run these on commit)
  - Build executable (Windows): `.
    Build_AutoFire.ps1` or `.
    Build_AutoFire_Debug.ps1` which use `pyinstaller` and the spec files.

- Project-specific conventions
  - Black configured to 100 char line length (see `pyproject.toml`). Many long template strings in `app/main.py` intentionally exceed this — ignore E501 for those blocks.
  - Keep GUI code in `frontend/` / `app/`; algorithms in `cad_core/`; persistence and services in `backend/` (see `AGENTS.md`).
  - Small focused changes: prefer <300 line diffs and a feature branch per task (branch names like `feat/...`, `fix/...`).

- Tests and fast feedback
  - Tests use pytest and live under `tests/` (examples: `tests/frontend/test_tool_registry.py`, `tests/cad_core/*`).
  - Run the full test suite via your environment's pytest (activate venv first): `pytest -q`.

- Patterns & gotchas for code edits
  - Entrypoint import hack: `app/main.py` adjusts `sys.path` when run as script to allow `app.*` absolute imports. Preserve that behavior if refactoring entrypoints.
  - Optional modules: many dialogs and tools are imported inside try/except and fallback to simple stand-ins — changes should maintain graceful degradation.
  - Avoid module-level side effects. The repo explicitly avoids heavy module initialization; prefer factory functions and explicit setup (see `app/logging_config.py`).

- Integration points & external deps
  - GUI: PySide6 — heavy use of Qt widgets and QGraphicsScene. Tests often mock or avoid full GUI instantiation.
  - DXF import: `ezdxf` used in `app/dxf_import.py` and `cad_core` adapters.
  - Build: PyInstaller (`AutoFire.spec`) to bundle into an EXE; build scripts handle common issues (OneDrive paths, stale dist/build folders).

- Useful file references (examples to open)
  - `AGENTS.md` — human agent guide and repo principles.
  - `README.md` — quick-start, setup, build commands.
  - `pyproject.toml` — black/ruff config (line length 100, py311 target).
  - `app/main.py` — primary dev entrypoint; shows patterns for optional imports and GUI wiring.
  - `Build_AutoFire.ps1` / `setup_dev.ps1` — concrete build and setup flows.

- How to propose changes
  - Make small, focused PRs, run pre-commit locally, and include/adjust tests for logic changes.

If any section is unclear or you'd like more examples (CLI flags, a brief callgraph of `app/main.py`, or a list of frequently edited modules), say which one and I will expand it.
