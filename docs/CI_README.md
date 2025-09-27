# CI & Runners

This repository uses GitHub Actions for CI. The following workflows are provided under `.github/workflows/`:

- `ci.yml` — combined CI that includes `smoke-windows`, `test-matrix`, `lint`, and `package` jobs.
- `ci_run_smoke_windows.yml` — separate smoke workflow that runs the headless `run_logs` runner on `windows-latest`.

Local smoke test

To run the headless smoke runner locally:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
py -3 -m run_logs.run_all_simulations
```

CI notes

- `test-matrix` runs on both `ubuntu-latest` and `windows-latest`. Linux runs pytest under `xvfb-run`.
- `lint` runs `ruff check .`. Add other linters to the workflow as needed.
- `package` builds `sdist` and `wheel` on tag pushes and uploads artifacts.
