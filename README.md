# AutoFireBase

Overview
- Python app with CAD-style drawing tools and packaging via PyInstaller.
- This repo now includes standard Python hygiene: .gitignore, formatting, linting, and pre-commit hooks.

Prerequisites
- Python 3.11 (recommended), Git, PowerShell on Windows.

Quick Start (Windows, PowerShell)
- Clone and open this repo.
- Run: `./setup_dev.ps1` (creates `.venv`, installs requirements, sets up pre-commit).
- Activate later: `. .venv/Scripts/Activate.ps1`
- Run the app: `python main.py`
  - Alternative: `run_autofire.bat` or `.\run_autofire.ps1`
  - Legacy: `python app/main.py`

Features
- Separate Windows: Model Space and Paperspace as independent windows for better multi-monitor support.
- Project Overview: Central hub for notes, milestones, progress tracking, calendar, and AI assistance.
- AI Assistant: Natural language queries for drawing manipulation (currently simulation mode).
- CAD Tools: Draw, modify, measure, OSNAP, DXF/PDF import, device placement, coverage overlays.

Daily Workflow
- Activate venv: `. .venv/Scripts/Activate.ps1`
- Sync: `git pull` (ensure you’re on the correct branch).
- Code changes.
- Format/lint: `ruff check --fix .` and `black .` (pre-commit will also run these on commit).
- Commit: `git add -A && git commit -m "..."`
- Push: `git push` and open a PR.

Code Style & Tooling
- Black (line length 100) for formatting.
- Ruff for lint + import sorting; targets Python 3.11.
- Pre-commit runs Ruff + Black + basic whitespace fixes on commit.

Build
- Use the existing scripts: `Build_AutoFire.ps1` or `Build_AutoFire_Debug.ps1`.
- PyInstaller spec files (`AutoFire.spec`, `AutoFire_Debug.spec`) are kept in repo; build artifacts are ignored (`build/`, `dist/`).

Repo Hygiene
- Do not commit virtual envs, caches, `build/`, `dist/`, or backup files. Patterns are covered in `.gitignore`.
- Samples: the `Projects/` folder currently contains example assets (DXF/PDF/.autofire). Keep or move into a dedicated `samples/` folder in future if desired.

Contributing
- Branch from `main` using feature branches: `feat/<topic>` or `fix/<topic>`.
- Create small, focused PRs. The CI/tooling will enforce formatting and linting locally via pre-commit.
