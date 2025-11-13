# Automation Quickstart

This repo includes a simple automation setup to streamline routine work.

## VS Code tasks

- `setup: venv`: Run the project setup (creates .venv and installs deps).
- `format: ruff+black`: Auto-fix style/lint and format the repo.
- `test: pytest -q`: Run tests headlessly (uses the virtualenv if present).
- `lint+test`: Run formatting then tests as a composite.
- `run: app (dev)`: Launch the app with the venv activated.

Open Command Palette → "Tasks: Run Task" to use them.

## One-command PR (PowerShell)

Use the helper to create a branch, run lint/format/tests, push, and open a PR (if `gh` is installed):

```powershell
# From the repo root
./scripts/auto_pr.ps1 -Branch "chore/auto/<name>" -Draft
```

It will:

- Ensure a virtualenv (creates one via `setup_dev.ps1` if missing)
- Run `ruff --fix` and `black`
- Run `pytest -q`
- Create a branch, commit, push
- Open a draft PR with GitHub CLI (if installed)

## Tips

- Keep Copilot for inline suggestions; use a controller (Continue) or Cline for larger code edits. We recommend DeepSeek for fast codegen and Claude for longer reasoning.
- For tracing, set `AUTOFIRE_TRACING=1` and see `docs/TRACING.md`.
- On Windows PowerShell, chain commands with `;` instead of `&&`.
