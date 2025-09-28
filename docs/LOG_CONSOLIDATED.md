# Consolidated Logging Changelog

This document consolidates logging and ad-hoc `print(...)` messages found across the repository and provides a prioritized task list and recommendations for consolidation.

Summary
-------
- Central logger helper: `app/logging_config.setup_logging()` exists and is used by headless scripts.
- Many small scripts under `run_logs/` already use `logging`.
- There remain numerous `print(...)` occurrences across `scripts/`, `tools/`, and `scripts/archive/` (some are intentionally CLI-facing and should remain informational).
- Some `print(...)` instances live in `.venv` or third-party packages — skip these.

Files scanned (high level)
--------------------------
- run_logs/
  - `simulate_palette_selection.py` — logs selection keys, errors when no leaf found, calls existing handler.
  - `simulate_placement.py` — logs proto keys, scene coordinates, mouse event invocation and exceptions.
  - `simulate_tools_palette_and_mouse.py` — selection + synthesized mouse move/press/release; logs each step.
  - `run_all_simulations.py` — runner that runs the three simulators and returns non-zero on failure.

- app/
  - `logging_config.py` — central setup.
  - `main.py`, `main_fixed.py` — wired to setup logging and use module loggers.

- tools/
  - Various tools (e.g., `apply_inline_050_cadA.py`, `apply_patch.py`) contain `logging` and also `print(...)` used as user-facing output.

- scripts/
  - `scripts/archive/*` contains many archival helper scripts which emit progress via `print(...)`.

Recommendations and classification
----------------------------------
- Convert development/debug `print(...)` into `logger.debug/info/warning/error/exception` depending on severity.
- Keep concise, user-facing `print(...)` in CLI utilities that are intended to produce human-readable outputs OR convert them to `logger.info(...)` and ensure `setup_logging()` is invoked in CLI entry points.
- Exclude `.venv` and third-party packages from conversion.

Prioritized tasks
-----------------
1. Convert remaining `run_logs/` prints (done).
2. Convert small CLI tool prints in `tools/` and the top-level scripts (`fix_boot_dynamic_factory.py`, `test_app.py`, etc.) — small batch.
3. Review `scripts/archive/` and decide which scripts are part of the active toolchain; convert where useful.
4. Add CI tasks to run the simulator runner and a print-scan check to prevent regressions.

Appendix: Example conversions
----------------------------
- print("Error: ", e)  ->  logger.exception("Error while X: %s", e)
- print('Done.')        ->  logger.info('Done.')  (add `setup_logging()` to entrypoint)


Generated: consolidated by automated scan — use as the basis for CI tasks and PRs.
