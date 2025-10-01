# Contributing Guide

Setup
- Windows PowerShell: `./setup_dev.ps1`
- Activate: `. .venv/Scripts/Activate.ps1`
 - Quick tests (CI) use a small set of dev requirements; see `requirements-dev-minimal.txt` for the minimal list used by the quick-tests workflow.

Workflow
- Create an issue; agree on scope/acceptance criteria.
- Branch: `git checkout -b feat/<name>`
- Code with tests: `pytest -q`
- Format/lint: `ruff check --fix . && black .`
- Commit/push; open PR; link the issue.

Standards
- Docstrings for public functions/classes; type hints on new code.
- Prefer pure functions in `cad_core/`; side effects in `frontend/` only.
- Keep PRs small and focused; update docs when behavior changes.
