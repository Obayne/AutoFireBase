# AutoFireBase

[![CI](https://github.com/Obayne/AutoFireBase/workflows/CI/badge.svg)](https://github.com/Obayne/AutoFireBase/actions/workflows/ci.yml)
[![Release](https://github.com/Obayne/AutoFireBase/workflows/Release/badge.svg)](https://github.com/Obayne/AutoFireBase/actions/workflows/release.yml)

Overview
- Python app with CAD-style drawing tools and packaging via PyInstaller.
- This repo now includes standard Python hygiene: .gitignore, formatting, linting, and pre-commit hooks.
- Fully automated GitHub workflows for CI/CD, dependency management, and more.

Prerequisites
- Python 3.11 (recommended), Git, PowerShell on Windows.
- **VS Code** (recommended) - See [VS Code Guide](docs/VS_CODE_GUIDE.md) for GUI-based workflow.

Quick Start (Windows, PowerShell)

**Option 1: VS Code (Recommended for GUI users)**
1. Clone this repo: `git clone https://github.com/Obayne/AutoFireBase.git`
2. Open `AutoFireBase.code-workspace` in VS Code
3. Install recommended extensions when prompted
4. Run task: `Setup Dev Environment` (Ctrl+Shift+P → Tasks: Run Task)
5. Press F5 to run the app
6. See [VS Code Guide](docs/VS_CODE_GUIDE.md) for detailed instructions

**Option 2: Command Line**
- Clone and open this repo.
- Run: `./setup_dev.ps1` (creates `.venv`, installs requirements, sets up pre-commit).
- Activate later: `. .venv/Scripts/Activate.ps1`
- Run the app: `python app/main.py`
  - Alternative (new entry): `python -m frontend.app`

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
- **VS Code Users**: See [VS Code Guide](docs/VS_CODE_GUIDE.md) for GUI-based Git workflow.

## GitHub Automations

This repository includes comprehensive GitHub automation:

- **CI/CD**: Automatic testing, linting, and building on every push
- **Dependabot**: Weekly dependency updates (Mondays at 9 AM)
- **Auto-labeling**: PRs automatically labeled by size and type
- **Stale management**: Inactive issues/PRs automatically closed
- **Auto-merge**: PRs with `auto-merge` label merge after approval
- **Welcome bot**: First-time contributors get helpful welcome messages
- **Release automation**: Tagged commits trigger automatic builds and releases

**Learn More:**
- 📊 [Visual Automation Flow](docs/AUTOMATION_FLOW.md) - See how automation works
- 📖 [GitHub Automation Guide](docs/GITHUB_AUTOMATION.md) - Quick reference
- 💻 [VS Code Workflow Guide](docs/VS_CODE_GUIDE.md) - GUI-based development

See individual workflow files in `.github/workflows/` for details.
