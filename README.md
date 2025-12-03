# LV CAD (Low Volt Layer Vision)

Overview

- Python app with CAD-style drawing tools and Layer Vision intelligence for low voltage systems.
- Professional CAD layer analysis with exact device detection and coordinates.
- This repo now includes standard Python hygiene: .gitignore, formatting, linting, and pre-commit hooks.

Prerequisites

- Python 3.11 (recommended), Git, PowerShell on Windows.

Quick Start (Windows, PowerShell)

- Clone and open this repo.
- Run: `./setup_dev.ps1` (creates `.venv`, installs requirements, sets up pre-commit).
- Activate later: `. .venv/Scripts/Activate.ps1`
- Run the app: `python app/main.py`
  - Alternative (new entry): `python -m frontend.app`

Daily Workflow

- Activate venv: `. .venv/Scripts/Activate.ps1`
- Sync: `git pull` (ensure you're on the correct branch).
- Code changes.
- Format/lint: `ruff check --fix .` and `black .` (pre-commit will also run these on commit).
- Commit: `git add -A && git commit -m "..."`
- Push: `git push` and open a PR.

Automation

- One-command PR: `./scripts/auto_pr.ps1 -Branch "chore/auto/<name>" -Draft` (runs lint/test, commits, pushes, opens PR).
- Maintenance: `./scripts/auto_maintain.ps1 -Mode daily` (or weekly/full; can schedule with `-Schedule`).
- Release: `./scripts/auto_release.ps1 -Version "1.0.0"` (bumps version, builds, releases).
- Complete suite: `./scripts/auto_complete.ps1` (analyze, fix, test, build).
- See `docs/AUTOMATION.md` for details.

Code Style & Tooling

- Black (line length 100) for formatting.
- Ruff for lint + import sorting; targets Python 3.11.
- Pre-commit runs Ruff + Black + basic whitespace fixes on commit.

Build

- Use the existing scripts: `Build_LV_CAD.ps1` or `Build_LV_CAD_Debug.ps1`.
- PyInstaller spec files (`LV_CAD.spec`, `LV_CAD_Debug.spec`) handle the build process; build artifacts are ignored (`build/`, `dist/`).

Repo Hygiene

- Do not commit virtual envs, caches, `build/`, `dist/`, or backup files. Patterns are covered in `.gitignore`.
- Samples: the `Projects/` folder currently contains example assets (DXF/PDF/.lvcad). Keep or move into a dedicated `samples/` folder in future if desired.

Contributing

- Branch from `main` using feature branches: `feat/<topic>` or `fix/<topic>`.
- Create small, focused PRs. The CI/tooling will enforce formatting and linting locally via pre-commit.
