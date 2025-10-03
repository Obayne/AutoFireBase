# Contributing Guide

Setup
- Windows PowerShell: `./setup_dev.ps1`
- Activate: `. .venv/Scripts/Activate.ps1`
 - Quick tests (CI) use a small set of dev requirements; see `requirements-dev-minimal.txt` for the minimal list used by the quick-tests workflow.

CLI / entrypoint
- The package exposes a console script `autofire-cli` (entry point: `autofire.cli.__main__:main`).
- For development, run the CLI from the repo with:

	```powershell
	# run the placeholder CLI
	python -m autofire.cli --help
	# or use the helper which checks minimal deps first
	python scripts/cli_wrapper.py --help
	```

- To install the console script into your virtualenv (recommended for testing the installed behavior):

	```powershell
	. .venv/Scripts/Activate.ps1
	python -m pip install -e .
	autofire-cli --version
	```

If you prefer not to install, the `scripts/cli_wrapper.py` helper will verify the minimal runtime deps (`requirements-dev-minimal.txt`) and then delegate to `autofire.cli`.

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
