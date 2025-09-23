# Paperspace Minimal Mode

AutoFire supports a feature flag to run with a minimal Paperspace configuration for v1 testing and CI.

- Env var: `AF_PAPERSPACE_MODE`
  - `minimal` (default): disables Paperspace tabs and switching; app stays in Model space.
  - `full`: enables current Paperspace behavior (tabs, switching, default sheet).
- Qt app property: `AF_PAPERSPACE_MODE` is also set on the `QApplication` by `frontend/bootstrap.py`.

Behavior in minimal mode
- No default Paperspace sheet is created and the Layout tab remains on “Model”.
- Space selector/lock UI is hidden in the status bar.
- Calls to switch to Paperspace are no-ops; a status message is shown.

Where it’s wired
- `backend/config.py` exposes helpers for the flag.
- `frontend/bootstrap.py` sets the app property early on startup.
- `app/main.py` checks the app property and gates Paperspace tabs and switching.

CI configuration
- CI sets `QT_QPA_PLATFORM=offscreen` and `AF_PAPERSPACE_MODE=minimal` to run tests headlessly.

